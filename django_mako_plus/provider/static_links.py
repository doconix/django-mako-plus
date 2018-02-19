from django.conf import settings
from django.utils.module_loading import import_string

from ..util import merge_dicts, log
from ..version import __version__
from .base import BaseProvider

import logging
import os
import os.path
import json
import glob
from collections import namedtuple



FileInfo = namedtuple('FileInfo', ( 'url', 'mtime' ))

class LinkProvider(BaseProvider):
    '''
    Renders links like <link> and <script> based on the name of the template
    and supertemplates.

    Special format keywords for use in the options:
        {appname} - The app name for the template being rendered.
        {appdir} - The app directory for the template being rendered (full path).
        {template} - The name of the template being rendered, without its extension.
        {templatedir} - The directory of the current template (full path).
        {staticdir} - The static directory as defined in settings.
    '''
    # the default options are for CSS files
    default_options = merge_dicts(BaseProvider.default_options, {
        'group': 'static.file',
        'filename': '{appdir}/somedir/{template}.static.file',
    })
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matches = []
        file_pat = os.path.normpath(self.options_format(self.options['filename']))
        if log.isEnabledFor(logging.DEBUG):
            log.debug('%s searching for %s', self.__class__.__qualname__, file_pat)
        for fullpath in glob.iglob(file_pat):
            if log.isEnabledFor(logging.INFO):
                log.info('found %s', file_pat)
            self.matches.append(FileInfo(
                os.path.relpath(fullpath, settings.BASE_DIR).replace('\\', '/'),
                int(os.stat(fullpath).st_mtime),
            ))


class CssLinkProvider(LinkProvider):
    '''Generates a CSS <link>'''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'styles',
        'filename': '{appdir}/styles/{template}.css',
        'skip_duplicates': True,
    })

    def provide(self, provider_run, data):
        for fi in self.matches:
            provider_run.write('<link data-context="{contextid}" rel="stylesheet" type="text/css" href="{static}{url}?{version}" />'.format(
                contextid=provider_run.uid,
                static=settings.STATIC_URL,
                url=fi.url,
                version=provider_run.version_id if provider_run.version_id is not None else fi.mtime,
                skip_duplicates='true' if self.options['skip_duplicates'] else 'false',
            ))


class JsLinkProvider(LinkProvider):
    '''Generates a JS <script>.'''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'scripts',
        'filename': '{appdir}/scripts/{template}.js',
        'async': False,
    })

    def start(self, provider_run, data):
        data['urls'] = []

    def provide(self, provider_run, data):
        # delaying printing of tag because the JsContextProvider delays and this must go after it
        for fi in self.matches:
            data['urls'].append('{}?{}'.format(
                fi.url.replace('\\', '/'),
                provider_run.version_id if provider_run.version_id is not None else fi.mtime,
            ))

    def finish(self, provider_run, data):
        for url in data['urls']:
            provider_run.write('<script data-context="{contextid}" src="{static}{url}"{async}></script>'.format(
                contextid=provider_run.uid,
                static=settings.STATIC_URL,
                url=url,
                async=' async="async"' if self.options['async'] else '',
            ))


class JsContextProvider(BaseProvider):
    '''
    Adds all js_context() variables to DMP_CONTEXT.
    This should be listed before JsLinkProvider so the
    context variables are available during <script> runs.
    '''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'scripts',
        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoder = import_string(self.options['encoder'])
        self.template = "{}/{}".format(self.app_config.name, self.template_name)

    def start(self, provider_run, data):
        data['templates'] = []

    def provide(self, provider_run, data):
        data['templates'].append(self.template)

    def finish(self, provider_run, data):
        if len(data['templates']) == 0:
            return
        context_data = {
            jscontext('__router__'): {
                'template': self.template,
                'app': provider_run.request.dmp.app if provider_run.request is not None else None,
                'page': provider_run.request.dmp.page if provider_run.request is not None else None,
            },
        }
        for k in provider_run.context.kwargs:
            if isinstance(k, jscontext):
                value = provider_run.context[k]
                context_data[k] = value.__jscontext__() if hasattr(value, '__jscontext__') else value
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

