from django.conf import settings
from django.utils.module_loading import import_string

from ..uid import wuid
from ..util import merge_dicts, strip_whitespace
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
        'context_name': 'dmpScriptContext',
    })
    # Read "Bootstrap Script" section in docs/topics_css_js.rst for an explanation of these scripts
    context_source = strip_whitespace('''
        <script id="{contextid}">
            if (window["{contextname}"]===undefined){{
                window["{contextname}"]={{}};
            }}
            window.{contextname}["{contextid}"]={contextdata};
        </script>
    ''')
    script_source = strip_whitespace('''
        <script>
            (function(){{
                var n=document.createElement("script");
                n.id="{uid}";
                n.async={async};
                n.setAttribute("data-context", "{contextid}");
                n.src="{href}?{version}";
                if (document.currentScript) {{
                    document.currentScript.parentNode.insertBefore(n, document.currentScript.nextSibling);
                }}else{{
                    document.head.appendChild(n);
                }}
            }})();
        </script>
    ''')
    
    def init(self):
        super().init()
        self.encoder = import_string(self.options['encoder'])

    def get_content(self, provider_run):
        if self.href is None:
            return None
        script = self.script_source.format(
            uid=wuid(),           
            contextname=self.options['context_name'],
            contextid=provider_run.uid,  
            async='true' if self.options['async'] else 'false',
            href=self.href, 
            version=self.version_id,
        )
        # send the context with the first item
        if provider_run.chain_index == 0:
            context_data = { k: provider_run.context[k] for k in provider_run.context.kwargs if isinstance(k, jscontext) }
            context_script = self.context_source.format(
                contextname=self.options['context_name'],
                contextid=provider_run.uid,  
                contextdata=json.dumps(context_data, cls=self.encoder, separators=(',', ':')) if context_data else '{}',
            )
            return context_script + '\n' + script
        return script


class jscontext(str):
    '''
    Marks a key in the context dictionary as a JS context item.
    JS context items are sent to the template like normal,
    but they are also added to the runtime JS namespace.
    
    See the tutorial for more information on this function.
    '''
    # no code needed, just using the class for identity
    
