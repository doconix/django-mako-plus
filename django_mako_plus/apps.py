from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import engines



class Config(AppConfig):
    name = 'django_mako_plus'
    label = 'django_mako_plus'
    verbose_name = 'Django Mako Plus Templating Engine'

    def ready(self):
        '''Called by Django when the app is ready for use.'''
        # ensure the template engine has been loaded (on the Django shell, it doesn't load them until they are accessed.)
        for name in engines:
            engines[name]  # just accessing each one causes the load of each
