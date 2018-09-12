from django.apps import apps, AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import engines

from .defaults import DEFAULT_OPTIONS
from .provider.runner import init_provider_factories
from .signals import dmp_signal_register_app

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
        self.template_imports = [
            'import django_mako_plus',
            'import django.utils.html',     # used in template.py
        ]
        self.template_imports.extend(self.options['DEFAULT_TEMPLATE_IMPORTS'])

        # set up the static file providers
        self.provider_factories = init_provider_factories()

        # set up the parameter converters (can't import until apps are set up)
        from .converter.base import ParameterConverter
        ParameterConverter._sort_converters(app_ready=True)


    def register_app(self, app=None):
        '''
        Registers an app as a "DMP-enabled" app.  Normally, DMP does this
        automatically when included in urls.py.

        If app is None, the DEFAULT_APP is registered.
        '''
        app = app or self.options['DEFAULT_APP']
        if not app:
            raise ImproperlyConfigured('An app name is required because DEFAULT_APP is empty - please use a '
                                        'valid app name or set the DEFAULT_APP in settings')
        if isinstance(app, str):
            app = apps.get_app_config(app)

        # since this only runs at startup, this lock doesn't affect performance
        with self.registration_lock:
            # short circuit if already registered
            if app.name in self.registered_apps:
                return

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
