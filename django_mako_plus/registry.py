#####################################################
###   A registry of callable view functions
###   in the DMP system

from django.conf import settings
from django.apps import apps, AppConfig

from .router import router_factory
from .template import render_to_string_shortcut, render_shortcut
from .util import get_dmp_instance

import threading


# lock to keep register_app() and get_view() thread safe
rlock = threading.RLock()

# the DMP-enabled AppConfigs in the system
DMP_ENABLED_APPS = set()
# the cache of view functions
CACHED_VIEWS = {}


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
    Registers an app as a "DMP-enabled" app.  Registering creates a cached
    template renderer to make processing faster and adds the dmp_render()
    and dmp_render_to_string() methods to the app.   The app parameter can
    be either the name of the app or an AppConfig object.

    This is called by MakoTemplates (engine.py) during system startup.
    '''
    if isinstance(app, str):
        app = apps.get_app_config(app)

    with rlock:
        # short circuit if already in the DMP_ENABLED_APPS
        if app.name in DMP_ENABLED_APPS:
            return

        # check for the DJANGO_MAKO_PLUS flag in the module
        if not getattr(app.module, 'DJANGO_MAKO_PLUS', False):
            return

        # first time for this app, so add to our dictionary
        # defaultdict, so no need to set to anything
        DMP_ENABLED_APPS.add(app.name)

        # set up the template, script, and style renderers
        # these create and cache just by accessing them
        get_dmp_instance().get_template_loader(app, 'templates', create=True)
        get_dmp_instance().get_template_loader(app, 'scripts', create=True)
        get_dmp_instance().get_template_loader(app, 'styles', create=True)

        # add the shortcut functions (only to the main templates, we don't do to scripts or styles
        # because people generally don't call those directly).  This is a monkey patch, but it is
        # an incredibly useful one because it makes calling app-specific rendering functions much
        # easier.
        #
        # Django's shortcut to return an *HttpResponse* is render(), and its template method to render a *string* is also render().
        # Good job on naming there, folks.  That's going to confuse everyone.  But I'm matching it to be consistent despite the potential confusion.
        app.module.dmp_render_to_string = render_to_string_shortcut(app.name)
        app.module.dmp_render = render_shortcut(app.name)



##############################################################
###   Retrieval of views from the registry.

def get_view(app_name, module_name, function_name, fallback_template):
    '''
    Retrieves the view function/class in the module: "app_name.views.module_name".
    If the module or function cannot be found, AttributeError is raised.
    The primary purpose of this method is to cache the views for quick routing.
    '''
    # first check the cache
    key = ( module_name, function_name )
    try:
        return CACHED_VIEWS[key]
    except KeyError:
        with rlock:
            # try again now that we're locked
            try:
                return CACHED_VIEWS[key]
            except KeyError:
                func = router_factory(app_name, module_name, function_name, fallback_template)
                if not settings.DEBUG:
                    CACHED_VIEWS[key] = func
                return func

    # the code should never be able to get here
    raise Exception("Django-Mako-Plus error: registry.get_view() should not have been able to get to this point.  Please notify the owner of the DMP project.  Thanks.")


