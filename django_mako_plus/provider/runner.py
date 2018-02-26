from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .base import BaseProvider
from ..util import DMP_OPTIONS, split_app, merge_dicts
from ..uid import wuid

import io


##################################################
###   Static File Provider Factory


def init_providers():
    '''Called when the DMP template engine is created by Django'''
    DMP_OPTIONS['RUNTIME_PROVIDER_FACTS'] = create_factories()


def create_factories(key='CONTENT_PROVIDERS'):
    '''Called from here as well as dmp_webpack.py'''
    providers = ( ProviderFactory(provider_def) for provider_def in DMP_OPTIONS[key] )
    return [ pf for pf in providers if pf.options['enabled'] ]


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

    def create(self, app_config, template_file):
        return self.provider_class(app_config, template_file, self.options)




####################################################
###   Main runner

# key to attach Provider objects to Mako Template objects during producting mode.
# I attach it to template objects because templates are already cached by mako, so
# caching them here would result in double-caching.
PROVIDERS_KEY = '_django_mako_plus_providers_'


class ProviderRun(object):
    '''A run through a template inheritance'''
    def __init__(self, tself, version_id=None, group=None, factories=None):
        self.uid = wuid()                           # a unique id for this run
        self.template = tself.template              # the template object
        self.request = tself.context.get('request') # request from the render()
        self.context = tself.context                # context from the render()
        self.group = group                          # the provider group being rendered (usually None)
        self.version_id = version_id                # unique number for overriding the cache (see LinkProvider)
        self._buffer = None                         # html to send back to the browser (providers add to this)
        # set up the factories we'll use
        if factories is None:
            factories = [
                pf for pf in DMP_OPTIONS['RUNTIME_PROVIDER_FACTS']
                if group is None or pf.options['group'] == group
            ]
        # provider data is separate from provider objects because a template (and its providers) can be in many chains at once,
        # such as base.htm's providers being in almost every chain on the site. this makes it unique to each provider on this run.
        self.provider_data = [ {} for i in range(len(factories)) ]
        # discover the ancestor templates for this template `self`
        self.chain = []
        # a set of providers for each template
        while tself is not None:
            # check if already attached to template, create if necessary
            providers = getattr(tself.template, PROVIDERS_KEY, None)
            if providers is None:
                app_config, template_file = split_app(tself.template.filename)
                if app_config is None:
                    raise ImproperlyConfigured("Could not determine the app for template {}. Is this template's app registered as a DMP app?".format(tself.template.filename))
                providers = [ pf.create(app_config, template_file) for pf in factories ]
                if not settings.DEBUG: # attach to template for speed in production mode
                    setattr(tself.template, PROVIDERS_KEY, providers)
            self.chain.append(providers)
            # loop with the next inherited template
            tself = tself.inherits
        # we need furthest ancestor first, current template last so current template (such as CSS) can override ancestors
        self.chain.reverse()

    def get_content(self):
        '''Runs the providers for each template in the current inheritance chain, returning the combined content.'''
        if len(self.chain) == 0:
            return ''
        self._buffer = io.StringIO()
        # start() on the last provider list in the chain
        for provider, data in zip(self.chain[-1], self.provider_data):
            provider.start(self, data)
        # provide() on the all provider lists in the chain
        for template_provider_list in self.chain:
            for provider, data in zip(template_provider_list, self.provider_data):
                provider.provide(self, data)
        # finish() on the last provider list in the chain
        for provider, data in zip(self.chain[-1], self.provider_data):
            provider.finish(self, data)
        return self._buffer.getvalue()

    def write(self, content):
        self._buffer.write(content)
        if settings.DEBUG:
            self._buffer.write('\n')
