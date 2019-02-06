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
        'create_entry': True,
        'link_attrs': {
            'async': False,
        },
        'skip_duplicates': True,
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

    def build_default_link(self):
        attrs = {}
        attrs["data-context"] = self.provider_run.uid
        attrs["src"] ="{}?{:x}".format(
            posixpath.join(
                settings.STATIC_URL,
                self.app_config.name,
                'scripts',
                '__bundle__.js',
            ),
            self.version_id,
        )
        attrs.update(self.options['link_attrs'])
        # attrs['onload'] = "DMP_CONTEXT.checkContextReady('{}')".format(self.provider_run.uid)
        return '<script{}></script>'.format(flatatt(attrs))

    def provide(self):
        # this must come after the regular JsLinkProvider script because the JsLinkProvider doesn't always
        # output a link (duplicates get skipped)
        super().provide()
        if self.is_last():
            self.write('<script data-context="{uid}">DMP_CONTEXT.callBundleContext("{uid}")</script>'.format(
                uid=self.provider_run.uid,
            ))
