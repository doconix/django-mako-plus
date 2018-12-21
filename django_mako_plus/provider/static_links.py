from django.conf import settings
from django.forms.utils import flatatt
from django.utils.module_loading import import_string

from ..util import crc32, getdefaultattr, log, merge_dicts
from ..version import __version__
from .base import BaseProvider

import logging
import os
import os.path
import json


#####################################################
###   Abstract Link Provider

class LinkProvider(BaseProvider):
    '''
    Renders links like <link> and <script> based on the name of the template
    and supertemplates.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filepath = self.calc_filepath()
        if log.isEnabledFor(logging.DEBUG):
            log.debug('%s searching for %s', repr(self), self.filepath)
        # file time and version hash
        try:
            self.mtime = int(os.stat(self.filepath).st_mtime)
            if log.isEnabledFor(logging.DEBUG):
                log.debug('%s found %s', repr(self), self.filepath)
            # version_id combines current time and the CRC32 checksum of file bytes
            self.version_id = (self.mtime << 32) | crc32(self.filepath)
        except FileNotFoundError:
            self.mtime = 0
            self.version_id = 0

    @property
    def default_options(self):
        return merge_dicts({
            # the static file path to look for and include (if exists) in
            # this should be `function(provider)` or `lambda provider: ...`
            # or if None, provider.calc_filepath() is called.
            'filepath': None,

            # if a template is rendered more than once in a request, should we link more than once?
            # defaults are: css=False, js=True, bundled_js=False
            'skip_duplicates': False,
        }, super().default_options)

    def calc_filepath(self, relpath=None):
        # in settings?
        if self.options['filepath']:
            return self.options['filepath'](self)
        # calculate it
        if self.app_config is None:
            log.warn('DMP static links provider skipped: template %s not in project subdir and `filepath` not in settings', self.template_relpath)
        if relpath is None:
            relpath = os.path.join('subdir', self.template_relpath) + '.ext'
        return os.path.join(
            settings.BASE_DIR if settings.DEBUG else settings.STATIC_ROOT,
            self.app_config.name,
            relpath,
        )

    def create_link(self, provider_run, data):
        '''
        If the file referenced in filepath() exists, this method is called
        to create the link to be included in the html.  Subclasses should
        provide an implementation for their type of file, such as
        <script> or <link>.
        '''
        return '<link rel="stylesheet" type="text/css" href="/web/path/to/file" />'

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
        filepath = self.filepath
        # delaying printing of tag to finish() because the JsContextProvider delays and this must go after it
        # short circuit if the file for this provider doesn't exist
        if self.mtime == 0:
            return
        # short circut if we're skipping duplicates and we've already seen this one
        if self.options['skip_duplicates']:
            if filepath in data['seen']:
                return
            data['seen'].add(filepath)
        # if we get here, this provider is enabled, so add it to the list
        data['enabled'].append(self)

    def finish(self, provider_run, data):
        for provider in data['enabled']:
            provider_run.write(provider.create_link(provider_run, data))



#############################################
###   Css and Js Link Providers


class CssLinkProvider(LinkProvider):
    '''Generates a CSS <link>'''
    FILE_SUBDIR = 'styles'
    FILE_EXT = '.css'

    @property
    def default_options(self):
        return merge_dicts({
            'group': 'styles',
            # if a template is rendered more than once in a request, we usually don't
            # need to include the css again.
            'skip_duplicates': True,
        }, super().default_options)

    def calc_filepath(self, relpath=None):
        return super().calc_filepath(relpath or os.path.join('styles', self.template_relpath) + '.css')

    def create_attrs(self, provider_run, data):
        '''Creates the attributes for the link (allows subclasses to add)'''
        attrs = {}
        attrs["data-context"] = provider_run.uid
        attrs["href"] ="{}?{:x}".format(
            os.path.join(
                settings.BASE_DIR if settings.DEBUG else settings.STATIC_ROOT,
                self.app_config.name,
                self.template_relpath.replace(os.path.sep, '/') + '.css',
            ),
            self.version_id,
        )
        return attrs

    def create_link(self, provider_run, data):
        '''Creates a link to the given URL'''
        attrs = self.create_attrs(provider_run, data)
        return '<link{} />'.format(flatatt(attrs))


class JsLinkProvider(LinkProvider):
    '''Generates a JS <script>.'''
    @property
    def default_options(self):
        return merge_dicts({
            'group': 'scripts',
            # if a template is rendered more than once in a request, we should link each one
            # so the script runs again each time the template runs
            'skip_duplicates': False,
            # whether to create an async script tag
            'async': False,
        }, super().default_options)

    def calc_filepath(self, relpath=None):
        return super().calc_filepath(relpath or os.path.join('scripts', self.template_relpath) + '.js')

    def create_attrs(self, provider_run, data):
        '''Creates the attributes for the link (allows subclasses to add)'''
        attrs = {}
        attrs["data-context"] = provider_run.uid
        attrs["src"] ="{}?{:x}".format(
            os.path.join(
                settings.BASE_DIR if settings.DEBUG else settings.STATIC_ROOT,
                self.app_config.name,
                self.template_relpath.replace(os.path.sep, '/') + '.js',
            ),
            self.version_id,
        )
        if self.options['async']:
            attrs['async'] = "async"
        return attrs

    def create_link(self, provider_run, data):
        '''Creates a link to the given URL'''
        attrs = self.create_attrs(provider_run, data)
        return '<script{}></script>'.format(flatatt(attrs))



###################################
###  JS Context Provider

class JsContextProvider(BaseProvider):
    '''
    Adds all js_context() variables to DMP_CONTEXT.
    This should be listed before JsLinkProvider so the
    context variables are available during <script> runs.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoder = import_string(self.options['encoder'])
        self.template = "{}/{}".format(self.app_config.name, self.template_relpath)

    @property
    def default_options(self):
        return merge_dicts({
            # the group this provider is part of.  this only matters when
            # the html page limits the providers that will be called with
            # ${ django_mako_plus.links(group="...") }
            'group': 'scripts',
            # the encoder to use for the JSON structure
            'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
        }, super().default_options)

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
        # add to the JS DMP_CONTEXT
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
