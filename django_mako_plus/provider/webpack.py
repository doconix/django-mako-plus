from django.conf import settings
from django.utils.module_loading import import_string

from ..util import merge_dicts, getdefaultattr
from ..version import __version__
from .static_links import LinkProvider

import os
import os.path
import json


EMPTY_SET = set()


class AppJsBundleProvider(LinkProvider):
    '''
    Generates a JS <script> for the app-level bundle.

    Special format keywords for use in the options:
        {appname} - The app name for the template being rendered.
        {template} - The name of the template being rendered, without its extension.
        {appdir} - The app directory for the template being rendered (full path).
        {staticdir} - The static directory as defined in settings.
    '''
    default_options = merge_dicts(LinkProvider.default_options, {
        'group': 'scripts',
        'filename': '{appdir}/scripts/__bundle__.js',
        'async': False,
    })

    def start(self, provider_run, data):
        data['scripts'] = []

    def provide(self, provider_run, data):
        # call the function for this view every time
        key = '{}/{}'.format(self.app_config.name, self.template_name)
        data['scripts'].append('if (DMP_CONTEXT.appBundles["%s"]) { DMP_CONTEXT.appBundles["%s"]() };' % (key, key))

    def finish(self, provider_run, data):
        '''Runs only on the main template in the chain.'''
        for fi in self.matches:
            # only print the first instance of a given href (one per request)
            js_done = getdefaultattr(provider_run.request, '__dmp_AppJsBundleProvider__', factory=set) if provider_run.request is not None else EMPTY_SET
            if fi.url not in js_done:
                provider_run.write('<script data-context="{contextid}" src="{static}{href}?{version}"{async}></script>'.format(
                    contextid=provider_run.uid,
                    static=settings.STATIC_URL,
                    href=fi.url,
                    version=provider_run.version_id if provider_run.version_id is not None else fi.mtime,
                    async=' async="async"' if self.options['async'] else '',
                ))
                js_done.add(fi.url)
        # print the script
        provider_run.write('<script data-context="{}">'.format(provider_run.uid))
        for line in data['scripts']:
            provider_run.write(line)
        provider_run.write('</script>')



