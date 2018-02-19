from ..command import run_command
from ..util import merge_dicts
from .base import BaseProvider

import os
import os.path
import shutil



class CompileProvider(BaseProvider):
    '''
    Compiles static files, such as *.scss or *.less, when an output file
    timestamp is older than the source file. In production mode, this check
    is done only once (the first time a template is run) per server start.

    Special format keywords for use in the options:
        {appname} - The app name for the template being rendered.
        {appdir} - The app directory for the template being rendered (full path).
        {template} - The name of the template being rendered, without its extension.
        {templatedir} - The directory of the current template (full path).
        {staticdir} - The static directory as defined in settings.
    '''
    # the command line should be specified as a list (see the subprocess module)
    default_options = merge_dicts(BaseProvider.default_options, {
        'group': 'styles',
        'source': '{appdir}/somedir/{template}.source',
        'target': '{appdir}/somedir/{template}.target',
        'needs_compile': lambda source, target: not os.path.exists(target) or os.stat(source).st_mtime > os.stat(target).st_mtime,
        'command': [ 'echo', '{appdir}/somedir/{template}.source', '{appdir}/somedir/{template}.target' ],
    })
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        source_path = self.options_format(self.options['source'])
        if os.path.exists(source_path):
            target_path = self.options_format(self.options['target'])
            if self.options['needs_compile'](source_path, target_path):
                run_command(*[ self.options_format(a) for a in self.options['command'] ])



class CompileScssProvider(CompileProvider):
    '''Specialized CompileProvider that contains settings for *.scss files.'''
    default_options = merge_dicts(CompileProvider.default_options, {
        'source': '{appdir}/styles/{template}.scss',
        'target': '{appdir}/styles/{template}.css',
        'command': [ shutil.which('scss'), '--load-path=.', '--unix-newlines', '{appdir}/styles/{template}.scss', '{appdir}/styles/{template}.css' ],
    })


class CompileLessProvider(CompileProvider):
    '''Specialized CompileProvider that contains settings for *.less files.'''
    default_options = merge_dicts(CompileProvider.default_options, {
        'source': '{appdir}/styles/{template}.less',
        'target': '{appdir}/styles/{template}.css',
        'command': [ shutil.which('lessc'), '--source-map', '{appdir}/styles/{template}.less', '{appdir}/styles/{template}.css' ],
    })

