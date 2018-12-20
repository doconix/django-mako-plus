
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

    def create_attrs(self, provider_run, data):
        attrs = super().create_attrs(provider_run, data)
        attrs['onload'] = "DMP_CONTEXT.checkBundle('{}')".format(provider_run.uid)
        return attrs

    def finish(self, provider_run, data):
        # this trigger call must be separate because script links may not always
        # render (duplicates are skipped)
        super().finish(provider_run, data)
        if len(data['enabled']) > 0:
            provider_run.write('<script data-context="{uid}">DMP_CONTEXT.triggerBundle("{uid}")</script>'.format(
                uid=provider_run.uid,
            ))
