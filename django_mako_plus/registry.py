#####################################################
###   A registry of callable view functions
###   in the DMP system

from django.apps import apps, AppConfig

from .template import render_to_string_shortcut_deprecated, render_to_response_shortcut_deprecated
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

        # DEPRECATED: will remove these module-level functions at some point
        #
        # add the shortcut functions (only to the main templates, we don't do to scripts or styles
        # because people generally don't call those directly).  This is a monkey patch, but it is
        # an incredibly useful one because it makes calling app-specific rendering functions much
        # easier.
        #
        # Django's shortcut to return an *HttpResponse* is render(), and its template method to render a *string* is also render().
        # Good job on naming there, folks.  That's going to confuse everyone.  But I'm matching it to be consistent despite the potential confusion.
        #
        app.module.dmp_render_to_string = render_to_string_shortcut_deprecated(app.name)
        app.module.dmp_render = render_to_response_shortcut_deprecated(app.name)


