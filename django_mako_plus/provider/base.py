from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.encoding import force_text

from ..util import DMP_OPTIONS, merge_dicts

import os
import os.path



##################################################
###   Static File Provider Factory


DEFAULT_CONTENT_PROVIDERS = [
    { 'provider': 'django_mako_plus.CssLinkProvider' },
    { 'provider': 'django_mako_plus.JsLinkProvider'  },
    { 'provider': 'django_mako_plus.JsContextProvider' },
]


def init_providers():
    '''Called when the DMP template engine is created by Django'''
    # these provider factories are used to create providers for the templates in the system
    DMP_OPTIONS['RUNTIME_PROVIDER_FACTS'] = [ ProviderFactory(provider_def) for provider_def in DMP_OPTIONS.get('CONTENT_PROVIDERS', DEFAULT_CONTENT_PROVIDERS) ]
    DMP_OPTIONS['RUNTIME_PROVIDER_FACTS'].sort(key=lambda pf: pf.options['weight'], reverse=True)


class ProviderFactory(object):
    '''Creator for a given Provider definition in settings.py.'''
    def __init__(self, provider_def):
        self.options = {}
        try:
            self.provider_class = provider_def['provider']
        except KeyError:
            raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py; a CONTENT_PROVIDERS item is missing `provider`.')
        if isinstance(self.provider_class, str):
            self.provider_class = import_string(self.provider_class)
        if not issubclass(self.provider_class, BaseProvider):
            raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py; The `provider` value must be a subclass of django_mako_plus.BaseProvider.')
        self.options = merge_dicts(self.provider_class.default_options, provider_def)

    def create(self, app_config, template_path, provider_index):
        return self.provider_class(app_config, template_path, self.options, provider_index)



##############################################################
###   Static File Providers

class BaseProvider(object):
    '''
    A list of provider instances is attached to each template in the system.
    During a provider run, all provider lists are run.

        base.htm      [ JsLinkProvider1, CssLinkProvider1, ... ]
           |
        app_base.htm  [ JsLinkProvider2, CssLinkProvider2, ... ]
           |
        index.html    [ JsLinkProvider3, CssLinkProvider3, ... ]

    The data argument sent into provide() spans a run vertically, meaning
    the three JsLinkProviders above share the same data dict.
    '''
    default_options = {
        'group': 'styles',
        'weight': 0,  # higher weights run first
    }
    def __init__(self, app_config, template_path, options, provider_index):
        self.app_config = app_config
        self.template_path = template_path
        # this next variable assumes the template is in the "normal" location: app/subdir/
        parts = os.path.splitext(self.template_path)[0].split(os.path.sep)
        self.template_name = os.path.sep.join(parts[1:]) if len(parts) > 1 else self.template_path
        self.options = merge_dicts(self.default_options, options)     # combined options dictionary
        self.provider_index = provider_index

    @property
    def group(self):
        return self.options['group']

    def provide(self, provider_run, data):
        '''Called on each provider for each template in a run - use provider_run.write() for content'''
        pass

    def format_string(self, val):
        '''
        Helper function that runs st.format with some standard named options.
        val.format() is called with {appname}, {appdir}, {template}.
        '''
        return force_text(val).format(
            appname=self.app_config.name,
            appdir=self.app_config.path,
            template=self.template_name,
        )

