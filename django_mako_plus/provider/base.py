from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
import os
from ..util import merge_dicts


##################################################
###   Static File Provider Factory

def init_provider_factories(key='CONTENT_PROVIDERS'):
    '''Called from apps.py when setting up'''
    factories = []
    dmp = apps.get_app_config('django_mako_plus')
    for index, provider_settings in enumerate(dmp.options.get(key, [])):
        fac = ProviderFactory(provider_settings, '_django_mako_plus_providers_{}_{}_'.format(key, index))
        factories.append(fac)
    return factories


class ProviderFactory(object):
    '''Creator for a given Provider definition in settings.py.'''
    def __init__(self, provider_settings, cache_key):
        self.cache_key = cache_key
        self.provider_settings = provider_settings
        try:
            self.provider_class = provider_settings['provider']
        except KeyError:
            raise ImproperlyConfigured('Invalid DMP CONTENT_PROVIDERS item in settings.py: missing `provider`')
        if isinstance(self.provider_class, str):
            self.provider_class = import_string(self.provider_class)
        if not issubclass(self.provider_class, BaseProvider):
            raise ImproperlyConfigured('Invalid DMP CONTENT_PROVIDERS item in settings.py: `provider` must reference a subclass of django_mako_plus.BaseProvider')

    def instance_for_template(self, template):
        '''Returns a provider instance for the given template'''
        # Mako already caches template objects, so I'm attaching the instance to the template for speed during production
        try:
            return getattr(template, self.cache_key)
        except AttributeError:
            pass

        # create and cache (if in prod mode)
        instance = self.provider_class(template, self.provider_settings)
        if not settings.DEBUG:
            setattr(template, self.cache_key, instance)
        return instance



##############################################################
###   Static File Provider Base

BASE_DEFAULT_OPTIONS = {
    # the group this provider is part of.  this only matters when
    # the html page limits the providers that will be called with
    # ${ django_mako_plus.links(group="...") }
    'group': 'styles',
    # whether enabled (see "Dev vs. Prod" in the DMP docs)
    'enabled': True,
}


class BaseProvider(object):
    '''
    Abstract base provider class.  An instance is tied to a template at runtime.

    Note that the app can only be inferred for templates in project apps (below settings.BASE_DIR).
    The app has to be inferred because mako creates templates internally during the render runtime,
    and I don't want to hack into Mako internals.

    Always set:
        self.template           Mako template object
        self.options            The combined options from the provider, its supers, and settings.py
        self.template_ext       Template extension.

    If app can be inferred (None if not):
        self.app_config         AppConfig the template resides in, if possible to infer.
        self.template_relpath   Template path, relative to app/templates/, without extension.
    '''
    def __init__(self, template, provider_settings):
        self.template = template
        self.app_config = None
        self.template_ext = None
        self.template_relpath = None
        if self.template.filename is not None:
            # try to infer the app
            fn_no_ext, self.template_ext = os.path.splitext(template.filename)
            relpath = os.path.relpath(fn_no_ext, settings.BASE_DIR)
            if not relpath.startswith('..'):  # can't infer reliably outside of project dir
                try:
                    path_parts = os.path.normpath(relpath).split(os.path.sep)
                    self.app_config = apps.get_app_config(path_parts[0])
                    self.template_relpath = '/'.join(path_parts[2:])
                except LookupError: # template isn't under an app
                    pass
        # combine the options
        self.options = merge_dicts(
            BASE_DEFAULT_OPTIONS,       # standard for all providers (hard coded above)
            self.default_options,       # from the provider class
            provider_settings           # from settings.py
        )

    @property
    def default_options(self):
        '''Subclasses should override this for default options specific to them.'''
        return {}

    def __repr__(self):
        return '<{}: {}/{}>'.format(
            self.__class__.__qualname__,
            self.app_config.name if self.app_config is not None else 'unknown',
            self.template_relpath if self.template_relpath is not None else self.template,
        )

    @property
    def group(self):
        return self.options['group']

    def start(self, provider_run, data):
        '''
        Called on the *main* template's provider list as the run starts.
        Initialize values in the data dictionary here.
        '''

    def provide(self, provider_run, data):
        '''Called on *each* template's provider list in the chain - use provider_run.write() for content'''

    def finish(self, provider_run, data):
        '''
        Called on the *main* template's provider list as the run finishes
        Finalize values in the data dictionary here.
        '''
