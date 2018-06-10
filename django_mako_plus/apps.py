from django.apps import AppConfig
from django.conf import settings
from django.template import engines
from django.utils.module_loading import import_string

from .defaults import DEFAULT_OPTIONS
from .engine import BUILTIN_CONTEXT_PROCESSORS
from .provider.runner import init_provider_factories

import itertools


class Config(AppConfig):
    name = 'django_mako_plus'
    label = 'django_mako_plus'
    verbose_name = 'Django Mako Plus Templating Engine'

    def ready(self):
        '''Called by Django when the app is ready for use.'''
        # set up the options
        self.options = {}
        self.options.update(DEFAULT_OPTIONS)
        for template_engine in settings.TEMPLATES:
            if template_engine.get('BACKEND', '').startswith('django_mako_plus'):
                self.options.update(template_engine.get('OPTIONS', {}))

        # the template engine
        self.engine =

        # default imports on every compiled template
        self.default_template_imports = [ 'import django_mako_plus' ]
        self.default_template_imports.extend(self.options['DEFAULT_TEMPLATE_IMPORTS'])

        # set up the static file providers
        self.providers = init_provider_factories()

        # set up the context processors
        context_processors = []
        for processor in itertools.chain(BUILTIN_CONTEXT_PROCESSORS, self.options['CONTEXT_PROCESSORS']):
            context_processors.append(import_string(processor))
        self.template_context_processors = tuple(context_processors)

        # set up the parameter converters (can't import until apps are set up)
        from .converter.base import ParameterConverter
        ParameterConverter._sort_converters(app_ready=True)
