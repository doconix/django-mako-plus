#####################################################
###   A registry of callable view functions
###   in the DMP system

from django.apps import apps, AppConfig
from django.core.exceptions import ImproperlyConfigured

from .util import get_dmp_instance, DMP_OPTIONS

import threading


# lock to keep register() thread safe
rlock = threading.RLock()

# the DMP-enabled AppConfigs in the system (by name)
DMP_ENABLED_APPS = {}


###############################################################
###   Registration functions for apps and view functions
###

def get_dmp_apps():
    '''Returns a sequence of DMP-enabled apps'''
    return DMP_ENABLED_APPS.values()


def is_dmp_app(app):
    '''
    Returns True if the given app is a DMP-enabled app.  The app parameter can
    be either the name of the app or an AppConfig object.
    '''
    if app is None:
        return False
    if isinstance(app, AppConfig):
        app = app.name
    return app in DMP_ENABLED_APPS


def ensure_dmp_app(app):
    '''Raises an AssertionException with a help mesage if the given app is not registered as a DMP app'''
    if not is_dmp_app(app):
        raise ImproperlyConfigured('''DMP's app-specific render functions were not placed on the request object. Likely reasons:
1) A template was rendered before the middleware's process_view() method was called (move after middleware call or use DMP's render_template() function which can be used anytime).
2) This app is not registered as a Django app (ensure the app is listed in `INSTALLED_APPS` in settings file).
3) This app is not registered as a DMP-enabled app (check `APP_DISCOVERY` in settings file or see DMP docs).''')



def register_dmp_app(app, inject_urls=False):
    '''
    Registers an app as a "DMP-enabled" app.  Normally, DMP does this
    automatically during system startup.

    If auto-discovery is disabled, call this method to register
    an app as DMP-enabled.  This should be done in the app's
    AppConfig.ready() method so registration happens *before* Django
    processes through urls.py.
    '''
    # this can only be done *before* django processes through urls.py
    if apps.ready:
        raise ImproperlyConfigured("App registration attempted too late in the startup process. "
                                   "Apps can no longer be registered with DMP because Django has already set up. "
                                   "Please call register_dmp_app() earlier in the process (ideally during AppConfig.ready() in yourapp/apps.py).")

    # since this only runs at startup, this lock doesn't affect performance
    if isinstance(app, str):
        app = apps.get_app_config(app)
    with rlock:
        # first time for this app, so add to our dictionary
        DMP_ENABLED_APPS[app.name] = app

        # set up the template, script, and style renderers
        # these create and cache just by accessing them
        get_dmp_instance().get_template_loader(app, 'templates', create=True)
        get_dmp_instance().get_template_loader(app, 'scripts', create=True)
        get_dmp_instance().get_template_loader(app, 'styles', create=True)
