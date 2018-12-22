from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from ..command import run_command
from ..util import merge_dicts
from .base import BaseProvider

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
    default_options = merge_dicts(BaseProvider.default_options, {
        'group': 'styles',
        # the source filename to search for
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}
        'sourcepath': os.path.join('styles', '{template}.scss'),
        # the destination filename to search for
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}, {sourcepath}
        'targetpath': os.path.join('styles', '{template}.css'),
        # the command to be run, as a list (see subprocess module)
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}, {sourcepath}, {targetpath}
        'command': [ 'echo', 'Subclasses should override this option' ],
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # since this is in the constructor, it runs only one time per server
        # run when in production mode
        if self.needs_compile:
            run_command(*self.build_command())

    @property
    def source(self):
        # we look for source files in the project directory
        # during both dev and prod
        return os.path.normpath(os.path.join(
            self.app_config.path,
            self.options['sourcepath'].format(
                basedir=settings.BASE_DIR,
                app=self.app_config.name,
                template=self.template,
                template_name=self.template_name,
                template_file=self.template_file,
                template_subdir=self.template_subdir,
            ),
        ))

    @property
    def target(self):
        # we output the target file to the project directory
        # during dev and to the static directory during prod
        if settings.DEBUG:
            return os.path.normpath(os.path.join(
                self.app_config.path,
                self.options['targetpath'].format(
                    basedir=settings.BASE_DIR,
                    app=self.app_config.name,
                    template=self.template,
                    template_name=self.template_name,
                    template_file=self.template_file,
                    template_subdir=self.template_subdir,
                    sourcepath=self.source,
                ),
            ))
        else:
            return os.path.normpath(os.path.join(
                settings.STATIC_ROOT,
                self.app_config.name,
                self.options['targetpath'].format(
                    basedir=settings.BASE_DIR,
                    app=self.app_config.name,
                    template=self.template,
                    template_name=self.template_name,
                    template_file=self.template_file,
                    template_subdir=self.template_subdir,
                    sourcepath=self.source,
                ),
            ))

    def build_command(self):
        '''Returns the command to run, as a list/tuple (see subprocess module)'''
        if not isinstance(self.options['command'], collections.Iterable) or isinstance(self.options['command'], (str, bytes)):
            raise ImproperlyConfigured('The `command` option on a compile provider must be a list')
        return [
            str(arg).format(
                basedir=settings.BASE_DIR,
                app=self.app_config.name,
                template=self.template,
                template_name=self.template_name,
                template_file=self.template_file,
                template_subdir=self.template_subdir,
                sourcepath=self.source,
                targetpath=self.target,
            )
            for arg in self.options['command']
        ]

    @property
    def needs_compile(self):
        try:
            source_mtime = os.stat(self.source).st_mtime
        except OSError:  # no source for this template, so just return
            return False
        try:
            target_mtime = os.stat(self.target).st_mtime
        except OSError: # target doesn't exist, so compile
            return True
        # both source and target exist, so compile if source newer
        return source_mtime > target_mtime


###################
###   Sass

class CompileScssProvider(CompileProvider):
    '''Specialized CompileProvider that contains settings for *.scss files.'''
    default_options = merge_dicts(CompileProvider.default_options, {
        # the source filename to search for
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        'sourcepath': os.path.join('styles', '{template}.scss'),
        # the destination filename to search for
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        'targetpath': os.path.join('styles', '{template}.css'),
        # the command to be run, as a list (see subprocess module)
        # codes: {app}, {template}, {template_name}, {template_file}, {template_subdir}, {sourcepath}, {targetpath}
        'command': [
            shutil.which('sass'),
            '--load-path=.',
            '{sourcepath}',
            '{targetpath}',
        ],
    })

    def build_command(self):
        # sass seems to need the target directory to exist
        targetdir = os.path.dirname(self.target)
        if not os.path.exists(targetdir):
            os.makedirs(targetdir)
        return super().build_command()




#####################
###   Less

class CompileLessProvider(CompileProvider):
    '''Specialized CompileProvider that contains settings for *.less files.'''
    default_options = merge_dicts(CompileProvider.default_options, {
        # the source filename to search for
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        'sourcepath': os.path.join('styles', '{template}.less'),
        # the destination filename to search for
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        'targetpath': os.path.join('styles', '{template}.css'),
        # the command to be run, as a list (see subprocess module)
        # codes: {app}, {template}, {template_name}, {template_file}, {template_subdir}, {sourcepath}, {targetpath}
        'command': [
            shutil.which('lessc'),
            '--source-map',
            '{sourcepath}',
            '{targetpath}',
        ],
    })
