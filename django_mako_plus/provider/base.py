from django.apps import apps
from django.conf import settings
import os, inspect
import logging
from ..util import log


TEMPLATE_ATTR_NAME = '_dmp_provider_cache_'

##############################################################
###   Abstract Provider Base

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
                                Usually this is just the template name, but could contain a subdirectory:
                                    homepage/templates/index.html       => "index"
                                    homepage/templates/forms/login.html => "forms/login"
    '''
    DEFAULT_OPTIONS = {
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'styles',
        # whether enabled (see "Dev vs. Prod" in the DMP docs)
        'enabled': True,
    }


    @classmethod
    def instance_for_template(cls, template, options):
        '''Returns an instance for the given template'''
        # Mako already caches template objects, so I'm attaching provider instances to templates
        provider_cache = getattr(template, TEMPLATE_ATTR_NAME, None)
        if provider_cache is None:
            provider_cache = {}
            setattr(template, TEMPLATE_ATTR_NAME, provider_cache)
        try:
            return provider_cache[options['_template_cache_key']]
        except KeyError:
            pass
        # not cached yet, so create the object
        instance = cls(template, options)
        if not settings.DEBUG:
            provider_cache[options['_template_cache_key']] = instance
        return instance


    def __init__(self, template, options):
        self.template = template
        self.options = options
        self.app_config = None
        self.template_ext = None
        self.template_relpath = None
        self.template_name = None
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
        return '<{}{}: {}/{}>'.format(
            self.__class__.__qualname__,
            '' if self.options['enabled'] else ' (disabled)',
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
