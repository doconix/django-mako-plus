from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import engines
from .util import set_dmp_option, get_dmp_option, log



class Config(AppConfig):
    name = 'django_mako_plus'
    label = 'django_mako_plus'
    verbose_name = 'Django Mako Plus Templating Engine'

    def ready(self):
        '''Called by Django when the app is ready for use.'''
        # ensure the template engine has been loaded (on the Django shell, it doesn't load them until they are accessed.)
        for name in engines:
            engines[name]  # just accessing each one causes the load of each

        # now that our engine has loaded, initialize a few parts of it
        # should we minify JS AND CSS FILES?
        set_dmp_option('RUNTIME_JSMIN', False)
        set_dmp_option('RUNTIME_CSSMIN', False)
        if get_dmp_option('MINIFY_JS_CSS', False) and not settings.DEBUG:
            try:
                from rjsmin import jsmin
            except ImportError:
                raise ImproperlyConfigured('MINIFY_JS_CSS = True in the Django Mako Plus settings, but the "rjsmin" package does not seem to be loaded.')
            try:
                from rcssmin import cssmin
            except ImportError:
                raise ImproperlyConfigured('MINIFY_JS_CSS = True in the Django Mako Plus settings, but the "rcssmin" package does not seem to be loaded.')
            set_dmp_option('RUNTIME_JSMIN', True)
            set_dmp_option('RUNTIME_CSSMIN', True)

        # should we compile SASS files?
        set_dmp_option('RUNTIME_SCSS_ENABLED', False)
        SCSS_BINARY = get_dmp_option('SCSS_BINARY', None)
        if isinstance(SCSS_BINARY, str):  # for backwards compatability
            log.warning('DMP :: Future warning: the settings.py variable SCSS_BINARY should be a list of arguments, not a string.')
            set_dmp_option('RUNTIME_SCSS_ARGUMENTS', SCSS_BINARY.split(' '))
            set_dmp_option('RUNTIME_SCSS_ENABLED', True)
        elif isinstance(SCSS_BINARY, (list, tuple)):
            set_dmp_option('RUNTIME_SCSS_ARGUMENTS', SCSS_BINARY)
            set_dmp_option('RUNTIME_SCSS_ENABLED', True)
        elif not SCSS_BINARY:
            set_dmp_option('RUNTIME_SCSS_ARGUMENTS', None)
            log.debug('DMP :: Sass integration not enabled.')
        else:
            raise ImproperlyConfigured('The SCSS_BINARY option in Django Mako Plus settings must be a list of arguments.  See the DMP documentation.')
