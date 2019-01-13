from django.apps import apps
from django.conf import settings
from django.utils.module_loading import import_string
from collections import namedtuple
import io
import logging
import inspect
from ..template import template_inheritance
from ..util import log, qualified_name
from ..uid import uid

# I can't keep the options inside the provider class itself because a given class
# can be listed more than once in settings.py (with different options).
# So instead I keep a list of the classes and their options here.
ProviderClassInfo = namedtuple("ProviderClassInfo", [ 'cls', 'options' ])

####################################################
###   Main runner for providers

class ProviderRun(object):
    '''A run through the providers for tself and its ancestors'''
    SETTINGS_KEY = 'CONTENT_PROVIDERS'
    CONTENT_PROVIDERS = []

    @classmethod
    def initialize_providers(cls):
        '''Initializes the providers (called from dmp app ready())'''
        dmp = apps.get_app_config('django_mako_plus')
        # regular content providers
        cls.CONTENT_PROVIDERS = []
        for provider_settings in dmp.options[cls.SETTINGS_KEY]:
            # import the class for this provider
            assert 'provider' in provider_settings, "Invalid entry in settings.py: CONTENT_PROVIDERS item must have 'provider' key"
            provider_cls = import_string(provider_settings['provider'])
            # combine options from all of its bases, then from settings.py
            options = {}
            for base in reversed(inspect.getmro(provider_cls)):
                options.update(getattr(base, 'DEFAULT_OPTIONS', {}))
            options.update(provider_settings)
            # add to the list
            if options['enabled']:
                # the index in the provider list is needed because a given class
                # can be listed more than once in settings.py (with different options)
                options['_template_cache_key'] = '_{}_{}_'.format(qualified_name(provider_cls), len(cls.CONTENT_PROVIDERS))
                cls.CONTENT_PROVIDERS.append(ProviderClassInfo(provider_cls, options))


    def __init__(self, tself, group=None):
        '''
        tself:              `self` object from a Mako template (available during rendering).
        group:              provider group to include (defaults to all groups if None)
        '''
        self.uid = uid(encode=True)     # the unique context id for this run
        self.request = tself.context.get('request')
        self.context = tself.context
        self.buffer = io.StringIO()

        # Create a table of providers for each template in the ancestry:
        #
        #     base.htm,      [ JsLinkProvider1, CssLinkProvider1, ... ]
        #        |
        #     app_base.htm,  [ JsLinkProvider2, CssLinkProvider2, ... ]
        #        |
        #     index.html,    [ JsLinkProvider3, CssLinkProvider3, ... ]
        self.template_providers = []
        for template in self.get_template_inheritance(tself):
            providers = []
            for pci in self.CONTENT_PROVIDERS:
                provider = pci.cls.instance_for_template(template, pci.options)
                if group is None or provider.group == group:
                    providers.append(provider)
            self.template_providers.append(providers)

        # Column-specific data dictionaries are maintained as the template providers run
        # (one per provider column).  These allow the provider instances of a given
        # column to share data if needed.
        #
        #      column_data = [ { col 1 }      , { col 2 }      , ... ]
        self.column_data = [ {} for pf in self.CONTENT_PROVIDERS ]


    def get_template_inheritance(self, tself):
        '''Returns a list of the template inheritance of tself, starting with the oldest ancestor'''
        return reversed(list(template_inheritance(tself)))


    def run(self):
        '''Performs the run through the templates and their providers'''
        # start() on tself (the last template in the list)
        for providers in self.template_providers[-1:]:
            for provider, data in zip(providers, self.column_data):
                provider.start(self, data)
        # provide() on the all provider lists in the chain
        for providers in self.template_providers:
            for provider, data in zip(providers, self.column_data):
                provider.provide(self, data)
        # finish() on tself (the last template in the list)
        for providers in self.template_providers[-1:]:
            for provider, data in zip(providers, self.column_data):
                provider.finish(self, data)


    def write(self, content):
        '''Provider instances use this to write to the buffer'''
        self.buffer.write(content)
        if settings.DEBUG:
            self.buffer.write('\n')


    def getvalue(self):
        '''Returns the buffer string'''
        return self.buffer.getvalue()
