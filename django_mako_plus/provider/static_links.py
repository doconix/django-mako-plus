from django.conf import settings
from django.utils.module_loading import import_string

from ..util import merge_dicts, flatten, log
from ..version import __version__
from .base import BaseProvider

import logging
import os
import os.path
import json
import glob
from collections import namedtuple



class LinkProvider(BaseProvider):
    '''
    Renders links like <link> and <script> based on the name of the template
    and supertemplates.
    '''
    # the default options are for CSS files
    default_options = merge_dicts(BaseProvider.default_options, {
        'group': 'static.file',
        # string for the absolute path to the filename that should be linked (if it exists)
        # if this is a function/lambda, DMP will run the function to get the string path
        'filename': 'app/subdir/template.ext',
    })
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        filepath = self.options['filename']
        if callable(filepath):  # if a function, call it to get the path
            filepath = filepath(self)
        self.filename = os.path.relpath(filepath, settings.BASE_DIR).replace('\\', '/')
        if log.isEnabledFor(logging.DEBUG):
            log.debug('[%s] %s searching for %s', self.template_file, self.__class__.__qualname__, self.filename)
        try:
            self.mtime = int(os.stat(filepath).st_mtime)
            if log.isEnabledFor(logging.INFO):
                log.info('[%s] found %s', self.template_file, self.filename)
        except FileNotFoundError:
            self.mtime = 0


class CssLinkProvider(LinkProvider):
    '''Generates a CSS <link>'''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'styles',
        'filename': lambda pr: os.path.join(*flatten(pr.app_config.path, 'styles', pr.subdir_parts[1:], pr.template_name + '.css')),
        'skip_duplicates': True,
    })

    def provide(self, provider_run, data):
        if self.mtime == 0:
            return
        provider_run.write('<link data-context="{contextid}" rel="stylesheet" type="text/css" href="{static}{url}?{version}" />'.format(
            contextid=provider_run.uid,
            static=settings.STATIC_URL,
            url=self.filename,
            version=provider_run.version_id if provider_run.version_id is not None else self.mtime,
            skip_duplicates='true' if self.options['skip_duplicates'] else 'false',
        ))


class JsLinkProvider(LinkProvider):
    '''Generates a JS <script>.'''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'scripts',
        'filename': lambda pr: os.path.join(*flatten(pr.app_config.path, 'scripts', pr.subdir_parts[1:], pr.template_name + '.js')),
        'async': False,
    })

    def start(self, provider_run, data):
        data['urls'] = []

    def provide(self, provider_run, data):
        # delaying printing of tag because the JsContextProvider delays and this must go after it
        if self.mtime == 0:
            return
        data['urls'].append('{}?{}'.format(
            self.filename.replace('\\', '/'),
            provider_run.version_id if provider_run.version_id is not None else self.mtime,
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
