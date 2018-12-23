from django.apps import apps
from django.conf import settings
from django.utils.module_loading import import_string
import io
import logging
from ..template import template_inheritance
from ..util import log
from ..uid import wuid


CONTENT_PROVIDERS = []
WEBPACK_COMMAND_PROVIDERS = []

def initialize_providers():
    '''Initializes the providers (called from dmp app ready())'''
    dmp = apps.get_app_config('django_mako_plus')
    # regular content providers
    for provider_settings in dmp.options['CONTENT_PROVIDERS']:
        assert 'provider' in provider_settings, "Invalid entry in settings.py: CONTENT_PROVIDERS item must have 'provider' key"
        cls = import_string(provider_settings['provider'])
        cls.initialize_options(provider_settings)
        if cls.OPTIONS['enabled']:
            CONTENT_PROVIDERS.append(cls)
    # special content providers list used during dmp_webpack management command
    for provider_settings in dmp.options['WEBPACK_PROVIDERS']:
        assert 'provider' in provider_settings, "Invalid entry in settings.py: CONTENT_PROVIDERS item must have 'provider' key"
        cls = import_string(provider_settings['provider'])
        cls.initialize_options(provider_settings)
        if cls.OPTIONS['enabled']:
            WEBPACK_COMMAND_PROVIDERS.append(cls)


####################################################
###   Main runner for providers

class ProviderRun(object):
    '''A run through the providers for tself and its ancestors'''
    def __init__(self, tself, group=None, provider_classes=None, ancestor_limit=0):
        '''
        tself:              `self` object from a Mako template (available during rendering).
        version_id:         hash/unique number to place on links
        group:              provider group to include (defaults to all groups if None)
        provider_classes:   list of provider factories to run on each template (defaults to settings.py if None)
        ancestors:          whether to recurse to ancestor templates
        '''
        dmp = apps.get_app_config('django_mako_plus')
        self.uid = wuid()           # a unique id for this run
        self.request = tself.context.get('request')
        self.context = tself.context
        if provider_classes is None:
            provider_classes = CONTENT_PROVIDERS
        self.buffer = io.StringIO()

        # Create a table of providers for each template in the ancestry:
        #
        #     base.htm,      [ JsLinkProvider1, CssLinkProvider1, ... ]
        #        |
        #     app_base.htm,  [ JsLinkProvider2, CssLinkProvider2, ... ]
        #        |
        #     index.html,    [ JsLinkProvider3, CssLinkProvider3, ... ]
        self.template_providers = []
        import pprint; pprint.pprint(provider_classes)
        for template in reversed(list(template_inheritance(tself, ancestor_limit))):
            providers = []
            for provider_class in provider_classes:
                provider = provider_class.instance_for_template(template)
                if group is None or provider.group == group:
                    providers.append(provider)
            self.template_providers.append(providers)

        # Column-specific data dictionaries are maintained as the template providers run
        # (one per provider column).  These allow the provider instances of a given
        # column to share data if needed.
        #
        #      column_data = [ { col 1 }      , { col 2 }      , ... ]
        self.column_data = [ {} for pf in provider_classes ]


    def run(self):
        '''Performs the run through the templates and their providers'''
        # start() on tself (the last template in the list)
        for providers in self.template_providers[-1:]:
            for provider, data in zip(providers, self.column_data):
                provider.start(self, data)
        # provide() on the all provider lists in the chain
        for providers in self.template_providers:
            for provider, data in zip(providers, self.column_data):
                if log.isEnabledFor(logging.DEBUG):
                    log.debug('%s running', repr(provider))
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
