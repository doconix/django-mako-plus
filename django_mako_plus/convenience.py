from .util import get_dmp_instance
import os, os.path


##############################################################
###   Convenience functions
###   These are imported into __init__.py

def get_template_loader(app, subdir='templates'):
    '''
    Convenience method that calls get_template_loader() on the DMP
    template engine instance.
    '''
    return get_dmp_instance().get_template_loader(app, subdir, create=True)


def get_template(app, template_name, subdir="templates"):
    '''
    Convenience method that retrieves a template given the app and
    name of the template.
    '''
    return get_dmp_instance().get_template_loader(app, subdir, create=True).get_template(template_name)


def render_template(request, app, template_name, context=None, subdir="templates", def_name=None):
    '''
    Convenience method that directly renders a template, given the app and template names.
    '''
    return get_template(app, template_name, subdir).render(context, request, def_name)


def get_template_loader_for_path(path, use_cache=True):
    '''
    Convenience method that calls get_template_loader_for_path() on the DMP
    template engine instance.
    '''
    return get_dmp_instance().get_template_loader_for_path(path, use_cache)


def get_template_for_path(path, use_cache=True):
    '''
    Convenience method that retrieves a template given a direct path to it.
    '''
    app_path, template_name = os.path.split(path)
    return get_dmp_instance().get_template_loader_for_path(app_path, use_cache=use_cache).get_template(template_name)


def render_template_for_path(request, path, context=None, use_cache=True, def_name=None):
    '''
    Convenience method that directly renders a template, given a direct path to it.
    '''
    return get_template_for_path(path, use_cache).render(context, request, def_name)
