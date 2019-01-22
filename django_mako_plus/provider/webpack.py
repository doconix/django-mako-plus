from django.conf import settings
from django.core.management import call_command
from django.forms.utils import flatatt
import os
import os.path
import posixpath
from ..util import merge_dicts
from .link import CssLinkProvider, JsLinkProvider
from ..management.commands.dmp_webpack import Command as WebpackCommand



class WebpackJsLinkProvider(JsLinkProvider):
    '''Generates a JS <script> tag for an app-level JS bundle file, if it exists.'''
    DEFAULT_OPTIONS = {
        'skip_duplicates': True,
        'async': False,
        'create_entry': True,
    }

    def build_default_filepath(self):
        # if development, recreate the entry file for this app
        if settings.DEBUG and self.options['create_entry']:
            call_command(WebpackCommand(running_inline=True), self.app_config.name, overwrite=True)

        # return the bundle path
        return os.path.join(
            self.app_config.name,
            'scripts',
            '__bundle__.js',
        )

    def build_default_link(self, provider_run, data):
        attrs = {}
        attrs["data-context"] = provider_run.uid
        attrs["src"] ="{}?{:x}".format(
            posixpath.join(
                settings.STATIC_URL,
                self.app_config.name,
                'scripts',
                '__bundle__.js',
            ),
            self.version_id,
        )
        attrs['onload'] = "DMP_CONTEXT.checkBundleLoaded('{}')".format(provider_run.uid)
        if self.options['async']:
            attrs['async'] = 'async'
        return '<script{}></script>'.format(flatatt(attrs))

    def finish(self, provider_run, data):
        # this trigger call must be separate because script links may not always
        # render (duplicates are skipped)
        super().finish(provider_run, data)
        if len(data['enabled']) > 0:
            provider_run.write('<script data-context="{uid}">DMP_CONTEXT.callBundleContext("{uid}")</script>'.format(
                uid=provider_run.uid,
            ))
