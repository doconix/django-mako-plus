from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.forms.utils import flatatt
import logging
import os
from ..util import crc32
from ..util import log
from .base import BaseProvider


DUPLICATES_KEY = '_LinkProvider_Filename_Cache_'

#####################################################
###   LinkProvider abstract base class

class LinkProvider(BaseProvider):
    '''
    Renders links like <link> and <script> based on the name of the template
    and supertemplates.
    '''
    DEFAULT_OPTIONS = {
        # the path to search for, relative to the project directory.  possible values are:
        #   1. None: a default path is used, such as "{app}/{subdir}/{filename.ext}", prefixed
        #      with the static root at production; see subclasses for their default filenames.
        #   2. function, lambda, or other callable: called as func(provider) and
        #      should return a string
        #   3. str: used directly
        'filepath': None,

        # the link to be inserted into the template. possible values:
        #   1. None: a default path is used, such as "<script src="..."></script>, prefixed
        #      with the static url at production; see subclasses for the default link format.
        #   2. function, lambda, or other callable: called as func(provider) and
        #      should return a string
        #   3. str: inserted directly into the template
        'link': None,

        # extra attributes for the link element
        'link_attrs': {},

        # if a template is rendered more than once in a request, should we link more than once?
        # defaults are: css=False, js=True, bundled_js=False
        'skip_duplicates': False,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.filepath, self.absfilepath, self.mtime, self.version_id = self.get_cache_item()

        except AttributeError:
            self.filepath = self.build_source_filepath()
            self.absfilepath = os.path.join(
                settings.BASE_DIR if settings.DEBUG else settings.STATIC_ROOT,
                self.filepath,
            )
            # file time and version hash
            try:
                self.mtime = int(os.stat(self.absfilepath).st_mtime)
                # version_id combines file modification time and the CRC32 checksum of file bytes
                self.version_id = (self.mtime << 32) | crc32(self.absfilepath)
            except FileNotFoundError:
                self.mtime = 0
                self.version_id = 0
            self.set_cache_item((self.filepath, self.absfilepath, self.mtime, self.version_id))

        if log.isEnabledFor(logging.DEBUG):
            log.debug('%s created for %s: [%s]', repr(self), self.filepath, 'will link' if self.mtime > 0 else 'will skip nonexistent file')


    ### Source Filepath Building Methods ###

    def build_source_filepath(self):
        # if defined in settings, run the function or return the string
        if self.options['filepath'] is not None:
            return self.options['filepath'](self) if callable(self.options['filepath']) else self.options['filepath']
        # build the default
        if self.app_config is None:
            log.warn('{} skipped: template %s not in project subdir and `filepath` not in settings', (self.__class__.__qualname__, self.template_relpath))
        return self.build_default_filepath()

    def build_default_filepath(self):
        # this method is overridden in CssLinkProvider and JsLinkProvider lower in this file
        raise ImproperlyConfigured('{} must set `filepath` in options (or a subclass can override build_default_filepath).'.format(self.__class__.__qualname__))


    ### Target Link Building Methods ###

    def build_target_link(self):
        # if defined in settings, run the function or return the string
        if self.options['link'] is not None:
            return self.options['link'](self) if callable(self.options['link']) else self.options['link']
        # build the default
        if self.app_config is None:
            log.warn('{} skipped: template %s not in project subdir and `sourcepath` not in settings', (self.__class__.__qualname__, self.template_relpath))
        return self.build_default_link()

    def build_default_link(self):
        # this method is overridden in CssLinkProvider and JsLinkProvider lower in this file
        raise ImproperlyConfigured('{} must set `link` in options (or a subclass can override build_default_link).'.format(self.__class__.__qualname__))


    ### Provider Run Methods ###

    def get_already_generated(self):
        # try to cache in the request, but if request is None, use the provider run
        # note that the single key string skips duplicates across different instances, not just within this instance
        placeholder = self.provider_run.request.dmp if self.provider_run.request is not None else self.provider_run
        try:
            return getattr(placeholder, DUPLICATES_KEY)
        except AttributeError:
            cache = set()
            setattr(placeholder, DUPLICATES_KEY, cache)
            return cache

    def provide(self):
        # short circuit if the file doesn't exist
        if self.mtime == 0:
            return
        # short circut if we're skipping duplicates and we've already seen this one
        if self.options['skip_duplicates']:
            already_generated = self.get_already_generated()
            if self.absfilepath in already_generated:
                if log.isEnabledFor(logging.DEBUG):
                    log.debug('%s skipped duplicate %s', repr(self), self.filepath)
                return
            already_generated.add(self.absfilepath)

        # if we get here, generate the link
        if log.isEnabledFor(logging.DEBUG):
            log.debug('%s linking %s', repr(self), self.filepath)
        self.write(self.build_target_link())


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
        '''Called when 'filepath' is not defined in the settings'''
        return os.path.join(
            self.app_config.name,
            'styles',
            self.template_relpath + '.css',
        )

    def build_default_link(self):
        '''Called when 'link' is not defined in the settings'''
        attrs = {}
        attrs["rel"] = "stylesheet"
        attrs["href"] ="{}?{:x}".format(
            os.path.join(settings.STATIC_URL, self.filepath).replace(os.path.sep, '/'),
            self.version_id,
        )
        attrs.update(self.options['link_attrs'])
        attrs["data-context"] = self.provider_run.uid       # can't be overridden
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
    }

    def build_default_filepath(self):
        '''Called when 'filepath' is not defined in the settings'''
        return os.path.join(
            self.app_config.name,
            'scripts',
            self.template_relpath + '.js',
        )

    def build_default_link(self):
        '''Called when 'link' is not defined in the settings'''
        attrs = {}
        attrs["src"] = "{}?{:x}".format(
            os.path.join(settings.STATIC_URL, self.filepath).replace(os.path.sep, '/'),
            self.version_id,
        )
        attrs.update(self.options['link_attrs'])
        attrs["data-context"] = self.provider_run.uid       # can't be overridden
        return '<script{}></script>'.format(flatatt(attrs))
