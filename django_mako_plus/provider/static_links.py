from django.conf import settings
from django.utils.module_loading import import_string

from ..util import merge_dicts, flatten, log, crc32, getdefaultattr
from ..version import __version__
from .base import BaseProvider

import logging
import os
import os.path
import json
import glob
from collections import namedtuple


#####################################################
###   Abstract Link Provider

class LinkProvider(BaseProvider):
    '''
    Renders links like <link> and <script> based on the name of the template
    and supertemplates.
    '''


    # the default options are for CSS files
    default_options = merge_dicts(BaseProvider.default_options, {
        # subclasses should override the group
        'group': 'scripts',
        # how to process duplicate urls found across this request
        'skip_duplicates': False,
    })
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        path = self.filepath
        if log.isEnabledFor(logging.DEBUG):
            log.debug('[%s] %s searching for %s', self.template_file, self.__class__.__qualname__, path)
        # file time and version hash
        try:
            self.mtime = int(os.stat(path).st_mtime)
            if log.isEnabledFor(logging.INFO):
                log.info('[%s] found %s', self.template_file, path)
            # version_id combines current time and the CRC32 checksum of file bytes
            self.version_id = (self.mtime << 32) | crc32(path)
        except FileNotFoundError:
            self.mtime = 0
            self.version_id = 0


    @property
    def filepath(self):
        '''The path to the file on disk.  Subclasses may want to override this.'''
        return '/path/to/file'


    def create_link(self, provider_run, url):
        return '<link rel="stylesheet" type="text/css" href="/static/path/to/file" />'


    def start(self, provider_run, data):
        # add a set to the request (fallback to provider_run if request is None) for skipping duplicates
        if self.options['skip_duplicates']:
            data['seen'] = getdefaultattr(
                provider_run.request.dmp if provider_run.request is not None else provider_run,
                '_LinkProvider_Filename_Cache_',
                factory=set,
            )
        # enabled providers in the chain go here
        data['enabled'] = []


    def provide(self, provider_run, data):
        path = self.filepath
        # delaying printing of tag to finish() because the JsContextProvider delays and this must go after it

        # short circuit if the file for this provider doesn't exist
        if self.mtime == 0:
            return
        # short circut if we're skipping duplicates and we've already seen this one
        if self.options['skip_duplicates']:
            if path in data['seen']:
                return
            data['seen'].add(path)
        # if we get here, this provider is enabled, so add it to the list
        data['enabled'].append(self)


    def finish(self, provider_run, data):
        for provider in data['enabled']:
            provider_run.write(provider.create_link(provider_run))



#############################################
###   Css and Js Link Providers


class CssLinkProvider(LinkProvider):
    '''Generates a CSS <link>'''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'styles',
        # 'filename': lambda pr: os.path.join(*flatten(pr.app_config.path, 'styles', pr.subdir_parts[1:], pr.template_name + '.css')),
        'skip_duplicates': True,
    })

    @property
    def filepath(self):
        if settings.DEBUG:
            return os.path.join(*flatten(self.app_config.path, 'styles', self.subdir_parts[1:], self.template_name + '.css'))
        else:
            return os.path.join(*flatten(settings.STATIC_ROOT, self.app_config.name, 'styles', self.subdir_parts[1:], self.template_name + '.css'))

    def create_link(self, provider_run):
        '''Creates a link to the given URL'''
        if settings.DEBUG:
            relpath = os.path.relpath(self.filepath, settings.BASE_DIR)
        else:
            relpath = os.path.relpath(self.filepath, settings.STATIC_ROOT)
        return '<link data-context="{}" rel="stylesheet" type="text/css" href="{}{}?v={:x}" />'.format(
            provider_run.uid,
            settings.STATIC_URL,
            relpath.replace('\\', '/'),
            self.version_id,
        )


class JsLinkProvider(LinkProvider):
    '''Generates a JS <script>.'''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'scripts',
        # 'filename': lambda pr: os.path.join(*flatten(pr.app_config.path, 'scripts', pr.subdir_parts[1:], pr.template_name + '.js')),
        'async': False,
        'skip_duplicates': False,  # the JS may need to run each time it is included
    })

    @property
    def filepath(self):
        if settings.DEBUG:
            return os.path.join(*flatten(self.app_config.path, 'scripts', self.subdir_parts[1:], self.template_name + '.js'))
        else:
            return os.path.join(*flatten(settings.STATIC_ROOT, self.app_config.name, 'scripts', self.subdir_parts[1:], self.template_name + '.js'))

    def create_link(self, provider_run):
        '''Creates a link to the given URL'''
        if settings.DEBUG:
            relpath = os.path.relpath(self.filepath, settings.BASE_DIR)
        else:
            relpath = os.path.relpath(self.filepath, settings.STATIC_ROOT)
        return '<script data-context="{}" src="{}{}?v={:x}"{}></script>'.format(
            provider_run.uid,
            settings.STATIC_URL,
            relpath.replace('\\', '/'),
            self.version_id,
            ' async="async"' if self.options['async'] else '',
        )



###################################
###  JS Context Provider

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
