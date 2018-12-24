from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.forms.utils import flatatt
import logging
import os
import os.path
import posixpath
from ..util import crc32, getdefaultattr
from ..util import log
from .base import BaseProvider


#####################################################
###   LinkProvider abstract base class

class LinkProvider(BaseProvider):
    '''
    Renders links like <link> and <script> based on the name of the template
    and supertemplates.
    '''
    DEFAULT_OPTIONS = {
        # explicitly sets the path to search for - if this filepath exists, DMP
        # includes a link to it in the template. globs are not supported because this
        # should resolve to one exact file. possible values:
        #   1. None: a default path is used, such as "{app}/{subdir}/{filename.ext}", prefixed
        #      with the static root at production; see subclasses for their default filenames.
        #   2. function, lambda, or other callable: called as func(provider) and
        #      should return a string
        #   3. str: used directly
        'filepath': None,

        # explicitly sets the link to be inserted into the template (when filepath exists).
        # possible values:
        #   1. None: a default path is used, such as "<script src="..."></script>, prefixed
        #      with the static url at production; see subclasses for the default link format.
        #   2. function, lambda, or other callable: called as func(provider) and
        #      should return a string
        #   3. str: inserted directly into the template
        'link': None,

        # if a template is rendered more than once in a request, should we link more than once?
        # defaults are: css=False, js=True, bundled_js=False
        'skip_duplicates': False,
    }

    def __init__(self, template, options):
        super().__init__(template, options)
        self.filepath = os.path.join(
            settings.BASE_DIR if settings.DEBUG else settings.STATIC_ROOT,
            self.build_source_filepath()
        )
        # file time and version hash
        try:
            self.mtime = int(os.stat(self.filepath).st_mtime)
            # version_id combines current time and the CRC32 checksum of file bytes
            self.version_id = (self.mtime << 32) | crc32(self.filepath)
        except FileNotFoundError:
            self.mtime = 0
            self.version_id = 0
        if log.isEnabledFor(logging.DEBUG):
            log.debug('%s created for %s: [%s]', repr(self), self.filepath, 'will link' if self.mtime > 0 else 'will skip nonexistent file')


    ### Source Filepath Building Methods ###

    def build_source_filepath(self):
        # if defined in settings, run the function or return the string
        if self.options['filepath'] is not None:
            return self.options['filepath'](self) if callable(self.options['filepath']) else self.options['filepath']
        # build the default
        if self.app_config is None:
            log.warn('{} skipped: template %s not in project subdir and `targetpath` not in settings', (self.__class__.__qualname__, self.template_relpath))
        return self.build_default_filepath()

    def build_default_filepath(self):
        raise ImproperlyConfigured('{} must set `filepath` in options (or a subclass can override build_default_filepath).'.format(self.__class__.__qualname__))


    ### Target Link Building Methods ###

    def build_target_link(self, provider_run, data):
        # if defined in settings, run the function or return the string
        if self.options['link'] is not None:
            return self.options['link'](self) if callable(self.options['link']) else self.options['link']
        # build the default
        if self.app_config is None:
            log.warn('{} skipped: template %s not in project subdir and `targetpath` not in settings', (self.__class__.__qualname__, self.template_relpath))
        return self.build_default_link(provider_run, data)

    def build_default_link(self, provider_run, data):
        raise ImproperlyConfigured('{} must set `link` in options (or a subclass can override build_default_link).'.format(self.__class__.__qualname__))


    ### Provider Run Methods ###

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
                if log.isEnabledFor(logging.DEBUG):
                    log.debug('%s skipped duplicate %s', repr(self), self.filepath)
                return
            data['seen'].add(filepath)
        # if we get here, this provider is enabled, so add it to the list
        if log.isEnabledFor(logging.DEBUG):
            log.debug('%s linking %s', repr(self), self.filepath)
        data['enabled'].append(self)

    def finish(self, provider_run, data):
        for provider in data['enabled']:
            provider_run.write(provider.build_target_link(provider_run, data))


#####################################
###  CssLinkProvider

class CssLinkProvider(LinkProvider):
    '''Generates a CSS <link>'''
    DEFAULT_OPTIONS = {
        'group': 'styles',
        # if a template is rendered more than once in a request, we usually don't
        # need to include the css again.
        'skip_duplicates': True,
    }

    def build_default_filepath(self):
        return os.path.join(
            self.app_config.name,
            'styles',
            self.template_relpath + '.css',
        )

    def build_default_link(self, provider_run, data):
        attrs = {}
        attrs['rel'] = 'stylesheet'
        attrs["data-context"] = provider_run.uid
        attrs["href"] ="{}?{:x}".format(
            # posixpath because URLs use forward slash
            posixpath.join(
                settings.STATIC_URL,
                self.app_config.name,
                'styles',
                self.template_relpath.replace(os.path.sep, '/') + '.css',
            ),
            self.version_id,
        )
        return '<link{} />'.format(flatatt(attrs))


##############################################
###   JsLinkProvider

class JsLinkProvider(LinkProvider):
    '''Generates a JS <script>.'''
    DEFAULT_OPTIONS = {
        'group': 'scripts',
        # if a template is rendered more than once in a request, we should link each one
        # so the script runs again each time the template runs
        'skip_duplicates': False,
        # whether to create an async script tag
        'async': False,
    }

    def build_default_filepath(self):
        return os.path.join(
            self.app_config.name,
            'scripts',
            self.template_relpath + '.js',
        )

    def build_default_link(self, provider_run, data):
        attrs = {}
        attrs["data-context"] = provider_run.uid
        attrs["src"] ="{}?{:x}".format(
            # posixpath because URLs use forward slash
            posixpath.join(
                settings.STATIC_URL,
                self.app_config.name,
                'scripts',
                self.template_relpath.replace(os.path.sep, '/') + '.js',
            ),
            self.version_id,
        )
        if self.options['async']:
            attrs['async'] = "async"
        return '<script{}></script>'.format(flatatt(attrs))
