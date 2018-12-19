
from ..util import merge_dicts
from .static_links import CssLinkProvider, JsLinkProvider
from .base import BaseProvider

import os
import os.path
import posixpath



class WebpackCssLinkProvider(CssLinkProvider):
    '''
    Generates a CSS <link> tag for the sitewide or app-level CSS bundle file, if it exists.
    '''
    default_options = merge_dicts(JsLinkProvider.default_options, {
        'filepath': os.path.join('styles', '__bundle__.css'),
        'skip_duplicates': True,
    })



class WebpackJsLinkProvider(JsLinkProvider):
    '''
    Generates a JS <script> tag for the sitewide or app-level JS bundle file, if it exists.
    In settings, this provider should be defined *before* WebpackJsCallProvider is defined.
    '''
    default_options = merge_dicts(JsLinkProvider.default_options, {
        'filepath': os.path.join('scripts', '__bundle__.js'),
        'skip_duplicates': True,
    })



class WebpackJsCallProvider(BaseProvider):
    '''
    Calls the app/page function(s) for the current template and its supertemplates.
    This provider is used when bundling page functions together into a single JS file.
    See the DMP docs regarding the use of webpack and __entry__.js files for more information.
    '''
    default_options = merge_dicts(BaseProvider.default_options, {
        'group': 'scripts',
    })


    def start(self, provider_run, data):
        data['funcs_to_run'] = []


    def provide(self, provider_run, data):
        # instead of adding a script tag for each template (like the JsLinkProider does),
        # we just need to trigger the function for this page from the function
        data['funcs_to_run'].append(posixpath.join(self.app_config.name, self.template))


    def finish(self, provider_run, data):
        '''Trigger the functions for the template inheritance.'''
        # using the `if` statement in the JS because the function will only
        # exist if a .js file actually existed in the scripts/ directory when
        # dmp_webpack command was run.
        provider_run.write('<script data-context="{contextid}">'.format(
            contextid=provider_run.uid,
        ))
        for template in data['funcs_to_run']:
            provider_run.write('if (DMP_CONTEXT.appBundles["%s"]) { DMP_CONTEXT.appBundles["%s"]() };' % (
                template,
                template
            ))
        provider_run.write('</script>')
