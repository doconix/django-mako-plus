#####################################################
###   A registry of callable view functions
###   in the DMP system

from django.apps import apps, AppConfig

from .util import get_dmp_instance

import threading


# lock to keep register_app() thread safe
rlock = threading.RLock()

# the DMP-enabled AppConfigs in the system (by name)
DMP_ENABLED_APPS = {}



###############################################################
###   Registration functions for apps and view functions
###

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


def register_app(app):
    '''
    Registers an app as a "DMP-enabled" app and creates a cached
    template renderer to make processing faster. The app parameter can
    be either the name of the app or an AppConfig object.

    This is called by MakoTemplates (engine.py) during system startup.
    '''
    if isinstance(app, str):
        app = apps.get_app_config(app)

    # since this only runs at startup, this lock doesn't affect performance
    with rlock:
        # short circuit if already in the DMP_ENABLED_APPS
        if app.name in DMP_ENABLED_APPS:
            return

        # check for the DJANGO_MAKO_PLUS flag in the module
        if not getattr(app.module, 'DJANGO_MAKO_PLUS', False):
            return

        # first time for this app, so add to our dictionary
        DMP_ENABLED_APPS[app.name] = app

        # set up the template, script, and style renderers
        # these create and cache just by accessing them
        get_dmp_instance().get_template_loader(app, 'templates', create=True)
        get_dmp_instance().get_template_loader(app, 'scripts', create=True)
        get_dmp_instance().get_template_loader(app, 'styles', create=True)

