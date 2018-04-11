from django.apps import AppConfig
from django.template import engines



class Config(AppConfig):
    name = 'django_mako_plus'
    label = 'django_mako_plus'
    verbose_name = 'Django Mako Plus Templating Engine'

    def ready(self):
        '''Called by Django when the app is ready for use.'''
        # ensure the DMP template engine has been loaded (the Django shell doesn't load it until it is accessed)
        # we just have to access the engine to cause the Django EngineHandler class to initialize it
        # Django calculates the alias/name based on its package, so it must be called django_mako_plus.
        # See the creation of EngineHandler.default_name in django.templates.util for this.
        engines['django_mako_plus']



