from ..command import run_command
from ..util import merge_dicts, flatten
from .base import BaseProvider

import os
import os.path
import shutil



class CompileProvider(BaseProvider):
    '''
    Runs a command, such as compiling *.scss or *.less, when an output file
    timestamp is older than the source file. In production mode, this check
    is done only once (the first time a template is run) per server start.

    Subclasses can override `source` and `target`, OR just override `needs_compile`.
    '''
    default_options = merge_dicts(BaseProvider.default_options, {
        'group': 'styles',
    })
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.needs_compile:
            run_command(*self.build_command())

    @property
    def source(self):
        return '/path/to/source.file'

    @property
    def target(self):
        return '/path/to/compiled/target.file'

    def build_command(self):
        '''Returns the command to run, as a list/tuple (see subprocess module)'''
        return ( 'echo', 'Subclasses should override this command.' )

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


class CompileScssProvider(CompileProvider):
    '''Specialized CompileProvider that contains settings for *.scss files.'''
    @property
    def source(self):
        # this inner
        return os.path.join(*flatten(self.app_config.path, 'styles', self.subdir_parts[1:], self.template_name + '.scss'))

    @property
    def target(self):
        return os.path.join(*flatten(self.app_config.path, 'styles', self.subdir_parts[1:], self.template_name + '.css'))

    def build_command(self):
        return (
            shutil.which('scss'),
            '--load-path=.',
            '--unix-newlines',
            self.source,
            self.target,
         )


class CompileLessProvider(CompileProvider):
    '''Specialized CompileProvider that contains settings for *.less files.'''
    @property
    def source(self):
        return os.path.join(*flatten(self.app_config.path, 'styles', self.subdir_parts[1:], self.template_name + '.less'))

    @property
    def target(self):
        return os.path.join(*flatten(self.app_config.path, 'styles', self.subdir_parts[1:], self.template_name + '.css'))

    def build_command(self):
        return (
            shutil.which('lessc'),
            '--source-map',
            self.source,
            self.target,
         )


