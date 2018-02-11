from ..util import merge_dicts
from .base import BaseProvider

import glob
import os
import os.path



class WebpackEntryProvider(BaseProvider):
    '''
    Creates app-level entry files for webpack.  You get one style file and
    one script file per app: styles/__entry__.css and scripts/__entry__.js.

    Special format keywords for use in the options:
        {appname} - The app name for the template being rendered.
        {appdir} - The app directory for the template being rendered (full path).
        {template} - The name of the template being rendered, without its extension.
    '''
    default_options = merge_dicts(BaseProvider.default_options, {
        'group': 'scripts',
        'target': '{appdir}/scripts/__entry__.js',  # the output file for entry into webpack
        'patterns': [                               # glob patterns to compile scripts from
            '{appdir}/scripts/*.js',
        ],
    })

    # def provide(self, provider_run, data):
    #     # we do a mini-run through


class WebpackCssEntryProvider(WebpackEntryProvider):
    default_options = merge_dicts(WebpackEntryProvider.default_options, {
        'group': 'styles',
        'target': '{appdir}/styles/__entry__.css',  # the output file for entry into webpack
        'patterns': [                               # glob patterns to compile scripts from
            '{appdir}/styles/*.css',
        ],
    })


class WebpackJsEntryProvider(WebpackEntryProvider):
    default_options = merge_dicts(WebpackEntryProvider.default_options, {
        'group': 'scripts',
        'target': '{appdir}/scripts/__entry__.js',  # the output file for entry into webpack
        'patterns': [                               # glob patterns to compile scripts from
            '{appdir}/scripts/*.js',
        ],
    })


