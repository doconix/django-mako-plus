from django.conf import settings

from ..util import merge_dicts, flatten
from .static_links import JsLinkProvider
from .base import BaseProvider

import os
import os.path
import posixpath



class WebpackJsLinkProvider(JsLinkProvider):
    '''
    Generates a JS <script> tag for the sitewide or app-level JS bundle file, if it exists.
    In settings, this provider should be defined *before* WebpackJsCallProvider is defined.
    (alternatively, sitewide or app bundle links can be included directly in base html templates).
    '''
    default_options = merge_dicts(JsLinkProvider.default_options, {
        'group': 'scripts',
        'filename': lambda pr: os.path.join(*flatten(pr.app_config.path, 'scripts', '__bundle__.js')),
        'async': False,
    })

    def finish(self, provider_run, data):
        # since we are doing a sitewide or app-level bundle, it will likely be in the list many times.
        # but it only needs to be included once.  otherwise the functionality is identical to JsLinkProvider
        added = set()
        data['urls'] = [url for url in data['urls'] if url not in added and not added.add(url)]
        super().finish(provider_run, data)




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
        data['templates'] = []


    def provide(self, provider_run, data):
        # instead of adding a script tag for each template (like the JsLinkProider does),
        # we just need to trigger the function for this page from the function
        data['templates'].append(posixpath.join(*flatten(self.app_config.name, self.subdir_parts[1:], self.template_name)))


    def finish(self, provider_run, data):
        '''Trigger the functions for the template inheritance.'''
        # using the `if` statement in the JS because the function will only
        # exist if a .js file actually existed in the scripts/ directory when
        # dmp_webpack command was run.
        provider_run.write('<script data-context="{contextid}">'.format(
            contextid=provider_run.uid,
        ))
        for template in data['templates']:
            provider_run.write('if (DMP_CONTEXT.appBundles["%s"]) { DMP_CONTEXT.appBundles["%s"]() };' % (
                template,
                template
            ))
        provider_run.write('</script>')
