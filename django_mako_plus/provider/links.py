from django.conf import settings
from django.utils.module_loading import import_string

from ..uid import wuid
from ..util import merge_dicts
from ..version import __version__
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
        'skip_duplicates': True,
    })
    def get_content(self, provider_run):
        if self.href is None:
            return None
        return '<link id="{uid}" data-context="{contextid}" rel="stylesheet" type="text/css" href="{href}?{version}" />'.format(
            uid=wuid(),           
            contextid=provider_run.uid,
            href=self.href, 
            version=self.version_id,
            skip_duplicates='true' if self.options['skip_duplicates'] else 'false',
        )


class JsLinkProvider(LinkProvider):
    '''Generates a JS <script>.'''
    default_options = merge_dicts(LinkProvider.default_options, {  
        'group': 'scripts',
        'filename': '{appdir}/scripts/{template}.js',
        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
        'async': False,
    })
    
    def init(self):
        super().init()
        self.encoder = import_string(self.options['encoder'])

    def get_content(self, provider_run):
        html = []
        # send the context with the first item
        if provider_run.chain_index == 0:
            context_data = { k: provider_run.context[k] for k in provider_run.context.kwargs if isinstance(k, jscontext) }
            html.append('<script>DMP_CONTEXT.set("{version}", "{contextid}", {data});</script>'.format(
                version=__version__,
                contextid=provider_run.uid,  
                data=json.dumps(context_data, cls=self.encoder, separators=(',', ':')) if context_data else '{}',
            ))
        if self.href is not None:
            html.append('<script>DMP_CONTEXT.addScript("{uid}", "{contextid}", "{app}/{template}", "{href}?{version}", {async});</script>'.format(
                uid=wuid(),           
                contextid=provider_run.uid,  
                app=self.app_name.replace('"', '\\"'),
                template=self.template_name.replace('"', '\\"'),
                href=self.href, 
                version=self.version_id,
                async='true' if self.options['async'] else 'false',
            ))
        return ('\n' if settings.DEBUG else '').join(html)


class jscontext(str):
    '''
    Marks a key in the context dictionary as a JS context item.
    JS context items are sent to the template like normal,
    but they are also added to the runtime JS namespace.
    
    See the tutorial for more information on this function.
    '''
    # no code needed, just using the class for identity
    
