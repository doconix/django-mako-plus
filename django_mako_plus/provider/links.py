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
        # subclasses override both of these
        'group': 'static.file',
        'filename': '{appdir}/somedir/{template}.static.file',
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fullpath = self.format_string(self.options['filename'])
        try:
            self.mtime = os.stat(fullpath)
            # make it relative to the project root, and ensure we have forward slashes (even on windows) because this is for urls
            self.href = posixpath.join(settings.STATIC_URL, os.path.relpath(fullpath, settings.BASE_DIR))
        except FileNotFoundError:
            self.mtime = None
            self.href = None


class CssLinkProvider(LinkProvider):
    '''Generates a CSS <link>'''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'styles',
        'filename': '{appdir}/styles/{template}.css',
        'skip_duplicates': True,
        'weight': 0,
    })

    def provide(self, provider_run, data):
        if self.href is None:
            return None
        provider_run.write('<link data-context="{contextid}" rel="stylesheet" type="text/css" href="{href}?{version}" />'.format(
            contextid=provider_run.uid,
            href=self.href,
            version=provider_run.version_id if provider_run.version_id is not None else self.mtime,
            skip_duplicates='true' if self.options['skip_duplicates'] else 'false',
        ))


class JsLinkProvider(LinkProvider):
    '''Generates a JS <script>.'''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'scripts',
        'filename': '{appdir}/scripts/{template}.js',
        'async': False,
        'weight': 4,  # see JsContextProvider
    })

    def provide(self, provider_run, data):
        # if the first template in the chain, set up a list for our urls
        if provider_run.chain_index == 0:
            data['urls'] = []
        # on every template in the chain, add the url if the file exists
        if self.href is not None:
            data['urls'].append('{}?{}'.format(
                self.href.replace('\\', '/'),
                provider_run.version_id if provider_run.version_id is not None else self.mtime,
            ))
        # on the last template, print all the urls we've collected
        if provider_run.chain_index == len(provider_run.chain) - 1 and len(data['urls']) > 0:
            provider_run.write('<script>')
            provider_run.write('DMP_CONTEXT.load("{contextid}", {urls}, {async});'.format(
                contextid=provider_run.uid,
                urls=json.dumps(data['urls']),
                async='true' if self.options['async'] else 'false',
            ))
            provider_run.write('</script>')


class JsContextProvider(BaseProvider):
    '''Adds all js_context() variables to DMP_CONTEXT'''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'scripts',
        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
        'weight': 5,  # must be higher than JsLinkProvider (context must come first so it is available when JS is loaded)
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoder = import_string(self.options['encoder'])
        self.template = "{}/{}".format(self.app_config.name, self.template_name)

    def provide(self, provider_run, data):
        # if the first template in the chain, set up a list for our templates
        if provider_run.chain_index == 0:
            data['templates'] = []
        # on every template in the chain, add the template
        data['templates'].append(self.template)
        # on the last template, print the context, including the list of templates we've collected
        if provider_run.chain_index == len(provider_run.chain) - 1 and len(data['templates']) > 0:
            context_data = {
                jscontext('__router__'): {
                    'template': self.template,
                    'app': provider_run.request.dmp.app if provider_run.request is not None else None,
                    'page': provider_run.request.dmp.page if provider_run.request is not None else None,
                },
            }
            context_data.update({ k: provider_run.context[k] for k in provider_run.context.kwargs if isinstance(k, jscontext) })
            provider_run.write('<script>')
            provider_run.write('DMP_CONTEXT.set("{version}", "{contextid}", {data}, {templates});'.format(
                version=__version__,
                contextid=provider_run.uid,
                data=json.dumps(context_data, cls=self.encoder, separators=(',', ':')) if context_data else '{}',
                templates=json.dumps(data['templates']),
            ))
            provider_run.write('</script>')


class jscontext(str):
    '''
    Marks a key in the context dictionary as a JS context item.
    JS context items are sent to the template like normal,
    but they are also added to the runtime JS namespace.

    See the tutorial for more information on this function.
    '''
    # no code needed, just using the class for identity

