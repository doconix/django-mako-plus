from django.apps import apps, AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import engines
from django.utils.module_loading import import_string

from .defaults import DEFAULT_OPTIONS
from .engine import BUILTIN_CONTEXT_PROCESSORS
from .provider.runner import init_provider_factories
from .signals import dmp_signal_register_app

import itertools
import threading


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

        # dmp-enabled apps registry
        self.registration_lock = threading.RLock()
        self.registered_apps = {}

        # init the template engine
        self.engine = engines['django_mako_plus']

        # default imports on every compiled template
        self.template_imports = [ 'import django_mako_plus' ]
        self.template_imports.extend(self.options['DEFAULT_TEMPLATE_IMPORTS'])

        # set up the static file providers
        self.provider_factories = init_provider_factories()

        # set up the context processors
        context_processors = []
        for processor in itertools.chain(BUILTIN_CONTEXT_PROCESSORS, self.options['CONTEXT_PROCESSORS']):
            context_processors.append(import_string(processor))
        self.template_context_processors = tuple(context_processors)

        # set up the parameter converters (can't import until apps are set up)
        from .converter.base import ParameterConverter
        ParameterConverter._sort_converters(app_ready=True)


    def register_app(self, app):
        '''
        Registers an app as a "DMP-enabled" app.  Normally, DMP does this
        automatically when included in urls.py.
        '''
        # since this only runs at startup, this lock doesn't affect performance
        if isinstance(app, str):
            app = apps.get_app_config(app)
        with self.registration_lock:
            # first time for this app, so add to our dictionary
            self.registered_apps[app.name] = app

            # set up the template, script, and style renderers
            # these create and cache just by accessing them
            self.engine.get_template_loader(app, 'templates', create=True)
            self.engine.get_template_loader(app, 'scripts', create=True)
            self.engine.get_template_loader(app, 'styles', create=True)

            # send the registration signal
            if self.options['SIGNALS']:
                dmp_signal_register_app.send(sender=self, app_config=app)


    def get_registered_apps(self):
        '''Returns a sequence of apps that are registered with DMP'''
        return self.registered_apps.values()


    def is_registered_app(self, app):
        '''Returns true if the given app/app name is registered with DMP'''
        if app is None:
            return False
        if isinstance(app, AppConfig):
            app = app.name
        return app in self.registered_apps


    def ensure_registered_app(self, app):
        '''Raises an AssertionException with a help mesage if the given app is not registered as a DMP app'''
        if not self.is_registered_app(app):
            raise ImproperlyConfigured('''DMP's app-specific render functions were not placed on the request object. Likely reasons:
    1) A template was rendered before the middleware's process_view() method was called (move after middleware call or use DMP's render_template() function which can be used anytime).
    2) This app is not registered as a Django app (ensure the app is listed in `INSTALLED_APPS` in settings file).
    3) This app is not registered as a DMP-enabled app (check `APP_DISCOVERY` in settings file or see DMP docs).''')
