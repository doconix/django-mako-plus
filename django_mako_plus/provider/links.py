from django.conf import settings
from django.utils.module_loading import import_string
from mako.filters import html_escape

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
        return '<link rel="stylesheet" type="text/css" href="{href}?{version}" />'.format(
            href=self.href, 
            version=self.version_id,
        )


class JsLinkProvider(LinkProvider):
    '''Generates a JS <script>'''
    default_options = merge_dicts(LinkProvider.default_options, {  
        'group': 'scripts',
        'filename': '{appdir}/scripts/{template}.js',
        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
        'async': True,
        'defer': False,
    })
    # A little explanation is in order for this dynamic script inclusion.
    # document.currentScript is available during the execution of a script
    # but *not* during callbacks. Some libraries (JQuery!) strip <script> tags
    # and execute them after insertion into the DOM, which makes currentScript
    # unavailable. With this approach, the <script> below can run inline or
    # in a callback, but the script loaded by the new tag always runs inline.
    # This way currentScript is available in all cases.
    script = ' '.join([ s.strip() for s in '''
        <script>
            var n=document.createElement("script");
            n.setAttribute("data-context", "{data}");
            n.setAttribute("async", {async});
            n.setAttribute("defer", {defer});
            n.src="{href}?{version}";
            document.body.appendChild(n);
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
            async='true' if self.options['async'] else 'false',
            defer='true' if self.options['defer'] else 'false',
            href=self.href, 
            version=self.version_id,
            data=json.dumps(js_context, cls=self.encoder).replace('"', '\\"'),
        )



class jscontext(str):
    '''
    Marks a key in the context dictionary as a JS context item.
    JS context items are sent to the template like normal,
    but they are also added to the runtime JS namespace.
    
    In myview.py:
        from django_mako_plus import js_context, view_function
        
        @view_function
        def myview(request):
            context = {
                jscontext('age'): 50,
                jscontext('name'): 'Homer Simpson',
                'another': 'sent only to template',
            }
            return request.dmp_render('myview.html', context)
    
    In myview.html:
        ${ django_mako_plus.links('scripts')
    Output in template:
        window.context = {
            "age": 50,
            "name": "Homer Simpson"
        };
    
    In myview.js:
        console.log(context.age);
    '''
    # no code needed, just using the class for identity
    pass
    
