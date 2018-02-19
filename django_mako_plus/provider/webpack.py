from django.conf import settings

from ..util import merge_dicts, getdefaultattr, flatten
from .static_links import LinkProvider

import os
import os.path
import posixpath


EMPTY_SET = set()


class AppJsBundleProvider(LinkProvider):
    '''
    Generates a JS <script> for the app-level bundle.
    '''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'scripts',
        'filename': lambda pr: os.path.join(*flatten(pr.app_config.path, 'scripts', '__bundle__.js')),
        'async': False,
    })

    def start(self, provider_run, data):
        data['templates'] = []

    def provide(self, provider_run, data):
        # instead of adding a script tag for each template (like the JsLinkProider does),
        # we just need to trigger the function for this page from the function
        data['templates'].append(posixpath.join(*flatten(self.app_config.name, self.subdir_parts[1:], self.template_name)))

    def finish(self, provider_run, data):
        '''Runs only on the main template in the chain.'''
        if self.mtime == 0 or len(data['templates']) == 0:
            return
        # add a <script> tag for the bundle (unless we already did so on this request)
        previous_bundles = getdefaultattr(provider_run.request.dmp, '__prev_app_bundles__', factory=set) if provider_run.request is not None else EMPTY_SET
        if self.filename not in previous_bundles:
            provider_run.write('<script data-context="{contextid}" src="{static}{href}?{version}"{async}></script>'.format(
                contextid=provider_run.uid,
                static=settings.STATIC_URL,
                href=self.filename,
                version=provider_run.version_id if provider_run.version_id is not None else self.mtime,
                async=' async="async"' if self.options['async'] else '',
            ))
            previous_bundles.add(self.filename)
        # trigger the functions for the template chain
        provider_run.write('<script data-context="{}">'.format(provider_run.uid))
        for template in data['templates']:
            provider_run.write('if (DMP_CONTEXT.appBundles["%s"]) { DMP_CONTEXT.appBundles["%s"]() };' % (template, template))
        provider_run.write('</script>')



