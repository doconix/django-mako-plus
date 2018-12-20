
from ..util import merge_dicts
from .static_links import CssLinkProvider, JsLinkProvider

import os
import os.path



class WebpackCssLinkProvider(CssLinkProvider):
    '''
    Generates a CSS <link> tag for the sitewide or app-level CSS bundle file, if it exists.
    '''
    default_options = merge_dicts(JsLinkProvider.default_options, {
        'group': 'styles',
        'filepath': os.path.join('styles', '__bundle__.css'),
        'skip_duplicates': True,
    })



class WebpackJsLinkProvider(JsLinkProvider):
    '''
    Generates a JS <script> tag for the sitewide or app-level JS bundle file, if it exists.
    In settings, this provider should be defined *before* WebpackJsCallProvider is defined.
    '''
    TEMPLATES_KEY = 'bundle_templates'
    default_options = merge_dicts(JsLinkProvider.default_options, {
        'filepath': os.path.join('scripts', '__bundle__.js'),
        'skip_duplicates': True,
        'async': True,
    })

    def finish(self, provider_run, data):
        '''Trigger the bundle functions for the template inheritance.'''
        super().finish(provider_run, data)
        provider_run.write('<script data-context="{contextid}">DMP_CONTEXT.execTemplateFunction("{contextid}");</script>'.format(
            contextid=provider_run.uid,
        ))
