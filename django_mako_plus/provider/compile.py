from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .base import BaseProvider
from ..util import log
from ..command import run_command

import os
import os.path
import shutil
import collections


class CompileProvider(BaseProvider):
    '''
    Runs a command, such as compiling *.scss or *.less, when an output file
    timestamp is older than the source file. In production mode, this check
    is done only once (the first time a template is run) per server start.

    When settings.DEBUG=True, checks for a recompile every request.
    When settings.DEBUG=False, checks for a recompile only once per server run.
    '''
    def __init__(self, template):
        super().__init__(template)
        self.sourcepath = os.path.join(settings.BASE_DIR if settings.DEBUG else settings.STATIC_ROOT, self.build_sourcepath())
        self.targetpath = os.path.join(settings.BASE_DIR if settings.DEBUG else settings.STATIC_ROOT, self.build_targetpath())
        # since this is in the constructor, it runs only one time per server
        # run when in production mode
        if self.needs_compile:
            if not os.path.exists(os.path.dirname(self.targetpath)):
                os.makedirs(os.path.dirname(self.targetpath))
            run_command(*self.build_command())

    DEFAULT_OPTIONS = {
        'group': 'styles',

        # explicitly sets the path to search for - if this filepath exists, DMP
        # includes a link to it in the template. globs are not supported because this
        # should resolve to one exact file. possible values:
        #   1. None: a default path is used, such as "{app}/{subdir}/{filename.ext}", prefixed
        #      with the static root at production; see subclasses for their default filenames.
        #   2. function, lambda, or other callable: called as func(provider) and
        #      should return a string
        #   3. str: used directly
        'sourcepath': None,

        # explicitly sets the path to search for - if this filepath exists, DMP
        # includes a link to it in the template. globs are not supported because this
        # should resolve to one exact file. possible values:
        #   1. None: a default path is used, such as "{app}/{subdir}/{filename.ext}", prefixed
        #      with the static root at production; see subclasses for their default filenames.
        #   2. function, lambda, or other callable: called as func(provider) and
        #      should return a string
        #   3. str: used directly
        'targetpath': None,

        # the command to be run, as a list (see subprocess module)
        'command': [ 'echo', 'Subclasses should override this option' ],
    }

    def build_sourcepath(self):
        # if defined in settings, run the function or return the string
        if self.OPTIONS['sourcepath'] is not None:
            return self.OPTIONS['sourcepath'](self) if callable(self.OPTIONS['sourcepath']) else self.OPTIONS['sourcepath']
        # build the default
        if self.app_config is None:
            log.warn('{} skipped: template %s not in project subdir and `targetpath` not in settings', (self.__class__.__qualname__, self.template_relpath))
        return self.build_default_sourcepath()

    def build_default_sourcepath(self):
        raise ImproperlyConfigured('{} must set `sourcepath` in options (or a subclass can override build_default_sourcepath).'.format(self.__class__.__qualname__))

    def build_targetpath(self):
        # if defined in settings, run the function or return the string
        if self.OPTIONS['targetpath'] is not None:
            return self.OPTIONS['targetpath'](self) if callable(self.OPTIONS['targetpath']) else self.OPTIONS['targetpath']
        # build the default
        if self.app_config is None:
            log.warn('{} skipped: template %s not in project subdir and `targetpath` not in settings', (self.__class__.__qualname__, self.template_relpath))
        return self.build_default_targetpath()

    def build_default_targetpath(self):
        raise ImproperlyConfigured('{} must set `targetpath` in options (or a subclass can override build_default_targetpath).'.format(self.__class__.__qualname__))

    @property
    def needs_compile(self):
        '''Returns True if self.sourcepath is newer than self.targetpath'''
        try:
            source_mtime = os.stat(self.sourcepath).st_mtime
        except OSError:  # no source for this template, so just return
            return False
        try:
            target_mtime = os.stat(self.targetpath).st_mtime
        except OSError: # target doesn't exist, so compile
            return True
        # both source and target exist, so compile if source newer
        return source_mtime > target_mtime

    def build_command(self):
        '''Returns the command to run, as a list (see subprocess module)'''
        # if defined in settings, run the function or return the string
        if self.OPTIONS['command'] is not None:
            return self.OPTIONS['command'](self) if callable(self.OPTIONS['command']) else self.OPTIONS['command']
        # build the default
        return self.build_default_targetpath()

    def build_default_command(self):
        raise ImproperlyConfigured('{} must set `command` in options (or a subclass can override build_default_command).'.format(self.__class__.__qualname__))


###################
###   Sass

class CompileScssProvider(CompileProvider):
    '''Specialized CompileProvider for SCSS'''
    def build_default_sourcepath(self):
        return os.path.join(
            self.app_config.name,
            'styles',
            self.template_relpath + '.scss',
        )

    def build_default_targetpath(self):
        # posixpath because URLs use forward slash
        return os.path.join(
            self.app_config.name,
            'styles',
            self.template_relpath + '.css',
        )

    def build_default_command(self):
        return [
            shutil.which('sass'),
            '--load-path={}'.format(settings.BASE_DIR),
            self.sourcepath,
            self.targetpath,
        ]


#####################
###   Less

class CompileLessProvider(CompileProvider):
    '''Specialized CompileProvider that contains settings for *.less files.'''
    def build_default_sourcepath(self):
        return os.path.join(
            self.app_config.name,
            'styles',
            self.template_relpath + '.less',
        )

    def build_default_targetpath(self):
        # posixpath because URLs use forward slash
        return os.path.join(
            self.app_config.name,
            'styles',
            self.template_relpath + '.css',
        )

    def build_default_command(self):
        return [
            shutil.which('lessc'),
            '--source-map',
            self.sourcepath,
            self.targetpath,
        ]
