from django.conf import settings
from django.utils.module_loading import import_string

from ..uid import wuid
from ..util import merge_dicts
from .base import BaseProvider

import os
import os.path
import posixpath
import json


class LinkProvider(BaseProvider):
    '''Base class for providers that create links'''
    # the default options are for CSS files
    default_options = merge_dicts(BaseProvider.default_options, {  
        'group': 'styles',
        'filename': '{appdir}/somedir/{template}.static.file',
    })
    def init(self):
        self.href = None
        fullpath = self.format_string(self.options['filename'])
        if os.path.exists(fullpath):
            # the version_id is a unique number either given by the project or by reading the last modified time of the file
            # it is important to add to links (see make_link in the subclasses) because it makes the url unique, which
            # forces browsers to re-download the file despite a previous version being in their cache.  Without this id,
            # some browsers (Chrome, I'm looking at you) use the cached version even after updates to the file.
            if self.version_id is None:
                self.version_id = int(os.stat(fullpath).st_mtime)
            # make it relative to the project root, and ensure we have forward slashes (even on windows) because this is for urls
            self.href = posixpath.join(settings.STATIC_URL, os.path.relpath(fullpath, settings.BASE_DIR))  

    def get_content(self, provider_run):
        return '<div class="DMP_LinkProvider">{}</div>'.format(self.href)


class CssLinkProvider(LinkProvider):
    '''Generates a CSS <link>'''
    default_options = merge_dicts(LinkProvider.default_options, { 
        'filename': '{appdir}/styles/{template}.css',
    })
    def get_content(self, provider_run):
        if self.href is None:
            return None
        return '<link rel="stylesheet" type="text/css" data-links="{linksid}" href="{href}?{version}" />'.format(
            linksid=provider_run.uid,
            href=self.href, 
            version=self.version_id,
        )


class JsLinkProvider(LinkProvider):
    '''Generates a JS <script>'''
    default_options = merge_dicts(LinkProvider.default_options, {  
        'group': 'scripts',
        'filename': '{appdir}/scripts/{template}.js',
        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
        'async': False,
    })
    #     A little explanation is in order for this dynamic script inclusion.
    # document.currentScript is available during the execution of a script
    # but *not* during callbacks. Front-end libraries like JQuery strip 
    # <script> tags on ajax because .innerHtml won't accept them, so the libraries
    # execute them after insertion into the DOM, which makes currentScript
    # unavailable.  We need currentScript because that's how context variables
    # get from <script data-context="..."> into the script.  
    #     With this approach, the <script> runs inline, via ajax, via callback, 
    # or any other way.  When the code is added to the DOM, the currentScript
    # variable is available in all cases.  We try to append directly after this 
    # bootstrap script, but fallback to append to <head> when in ajax or a callback.
    #     The only drawback to this approach is scripts added this way run
    # after all scripts in the original HTML, even when async=false. They do stay
    # in order, though, as long as async=False.
    script = ''.join([ s.strip() for s in '''
        <script>
            (function(){{
                var n=document.createElement("script");
                n.id="{uid}";
                n.async={async};
                n.setAttribute("data-inheritance", "{inheritanceid}");
                n.src="{href}?{version}";
                n.setAttribute("data-context", "{data}");
                if (document.currentScript) {{
                    document.currentScript.parentNode.insertBefore(n, document.currentScript.nextSibling);
                }}else{{
                    document.head.appendChild(n);
                }}
            }})();
        </script>
    '''.splitlines() ])
    
    def init(self):
        super().init()
        self.encoder = import_string(self.options['encoder'])

    def get_content(self, provider_run):
        if self.href is None:
            return None
        js_context = { k: provider_run.context[k] for k in provider_run.context.kwargs if isinstance(k, jscontext) }
        return self.script.format(
            uid=wuid(),                     # id="" is a unique id just to this tag
            inheritanceid=provider_run.uid, # data-inheritance="" is a shared id to all links in a template inheritance chain
            async='true' if self.options['async'] else 'false',
            href=self.href, 
            version=self.version_id,
            data=json.dumps(js_context, cls=self.encoder, separators=(',', ':')).replace('\\', '\\\\').replace('"', '\\"') if len(js_context) > 0 else '{}',
        )



class jscontext(str):
    '''
    Marks a key in the context dictionary as a JS context item.
    JS context items are sent to the template like normal,
    but they are also added to the runtime JS namespace.
    
    See the tutorial for more information on this function.
    '''
    # no code needed, just using the class for identity
    
