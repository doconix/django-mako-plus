#######################################################
###   This is the "main" method of DMP.
###   Django calls this automatically when starting up.
###   

from django.apps import AppConfig, apps
from django.core.exceptions import ImproperlyConfigured
from django_mako_plus.controller.router import register_dmp_app


class DMPConfig(AppConfig):
    name = 'django_mako_plus'
    verbose_name = "Django Mako Plus"
    
    def ready(self):
      '''Initialization code for the DMP app'''
      # go through the apps and see which are DMP-designated
      for config in get_dmp_app_configs():
        # add a renderer to the cache for this app
        register_dmp_app(config)

    

#################################################
###   Utility functions not meant to be used
###   outside this package.

def get_dmp_app_configs():
  '''Gets the DMP-enabled app configs, which will be a subset of all installed apps.  This is a generator function.'''
  for config in apps.get_app_configs():
    # check for the DJANGO_MAKO_PLUS = True in the app (should be in app/__init__.py)
    if getattr(config.module, 'DJANGO_MAKO_PLUS', False):
      yield config


