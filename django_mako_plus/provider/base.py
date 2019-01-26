from django.apps import apps
from django.conf import settings
import os, inspect
import logging
from ..util import log


##############################################################
###   Abstract Provider Base

class BaseProvider(object):
    '''
    Abstract base provider class.  Instances of this class are created by ProviderRun's constructor.

    Note that the app can only be inferred for templates in project apps (below settings.BASE_DIR).
    The app has to be inferred because mako creates templates internally during the render runtime,
    and I don't want to hack into Mako internals.
    '''
    DEFAULT_OPTIONS = {
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'styles',

        # whether enabled (see "Dev vs. Prod" in the DMP docs)
        'enabled': True,
    }

    def __init__(self, provider_run, template, index, options):
        # the following are always set
        self.provider_run = provider_run        # the object in charge of this run of providers for the given template
        self.template = template                # Mako template object
        self.index = index                      # position of this provider in the list for this run
        self.options = options                  # the combined options from the provider, its supers, and settings.py

        # the only time these remain None is if we can't infer the app. that happens when:
        #   1. the template was created from a string (and has no filename), or
        #   2. the template file is located outside of an app directory
        self.app_config = None              # AppConfig the template resides in, if possible to infer.
        self.template_ext = None            # Template filename extension
        self.template_relpath = None        # Template path, relative to app/templates/ and without extension, if possible to infer
        self.template_name = None           # Template filename without extension, if possible to infer
        if self.template.filename is not None:
            # try to infer the app
            fn_no_ext, self.template_ext = os.path.splitext(template.filename)
            relpath = os.path.relpath(fn_no_ext, settings.BASE_DIR)
            if not relpath.startswith('..'):  # can't infer reliably outside of project dir
                try:
                    path_parts = os.path.normpath(relpath).split(os.path.sep)
                    self.app_config = apps.get_app_config(path_parts[0])
                    self.template_relpath = '/'.join(path_parts[2:])
                    self.template_name = path_parts[-1]
                except LookupError: # template isn't under an app
                    pass

    def __repr__(self):
        return '<{}/{}:{}{}>'.format(
            self.app_config.name if self.app_config is not None else 'unknown',
            self.template_relpath if self.template_relpath is not None else self.template,
            self.__class__.__qualname__,
            '' if self.options['enabled'] else ' (disabled)',
        )

    @property
    def group(self):
        return self.options['group']

    def provide(self):
        '''
        Generate the content and do the work of this provider.
        Use self.write() to output content.
        '''
        pass

    def write(self, content):
        '''Writes content to the response'''
        # really just a redirect to the provider run
        self.provider_run.write(content)


    # in these next methods, the concept of "related providers" means the providers
    # of the same class type in the same position.
    # Suppose we have index.html inheriting from base.htm and we have three providers
    # listed in settings. We get six total providers:
    #
    #    base.htm   ->  JsContextProvider, CssLinkProvider, JsLinkProvider
    #       |
    #   index.html  ->  JsContextProvider, CssLinkProvider, JsLinkProvider
    #
    # In this example, the two JsContextProviders are "related providers",
    # the two CssLinkProviders are "related providers", and the two
    # JsLinkProviders are "related providers".

    def iter_related(self):
        '''
        Generator function that iterates this object's related providers,
        which includes this provider.
        '''
        for tpl in self.provider_run.templates:
            yield tpl.providers[self.index]

    def get_first(self):
        '''
        Returns the first provider in the related providers to this one.
        This is the provider instance for the base template (e.g. base.htm).
        This is useful when a provider class needs to do things at the start of a run.
        '''
        return self.provider_run.templates[0].providers[self.index]

    def is_first(self):
        '''
        Returns true if this provider is first to run among its related providers.
        This is the provider associated with the base template (e.g. base.htm).
        '''
        return self.provider_run.templates[0].template is self.template

    def get_last(self):
        '''
        Returns the last provider in the related providers to this one.
        This is the provider instance for the main template (e.g. index.html).
        This is useful when a provider class needs to do things at the end of a run.
        '''
        return self.provider_run.templates[-1].providers[self.index]

    def is_last(self):
        '''
        Returns true if this provider is last to run among its related providers.
        This is the provider associated with the main template (e.g. index.htm).
        '''
        return self.provider_run.templates[-1].template is self.template



    #  Each provider can cache one item in the template to make
    #  things faster at production. Raises an AttributeError if nothing has
    #  been cached.
    #
    #  Why store things in the template? Because Mako already uses a cache
    #  for templates, so this keeps the values alive as long as a template object is.
    #
    #  Note that:
    #   1. Values can't be stored in provider objects because new objects are created
    #      on each provider run.
    #   2. Values can't be stored as class variables because the same class can
    #      be listed more than once in settings.
    #   3. The options dict IS unique to a given provider entry, but there's no need
    #      to manage another cache there when Mako is doing it.

    def get_cache_item(self):
        '''Gets the cached item. Raises AttributeError if it hasn't been set.'''
        if settings.DEBUG:
            raise AttributeError('Caching disabled in DEBUG mode')
        return getattr(self.template, self.options['template_cache_key'])

    def set_cache_item(self, item):
        '''Sets the cached item'''
        setattr(self.template, self.options['template_cache_key'], item)
