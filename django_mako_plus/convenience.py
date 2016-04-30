from .util import get_dmp_instance
import os, os.path


##############################################################
###   Convenience functions
###   These are imported into __init__.py

def get_template_loader(app, subdir='templates', create=False):
    '''
    Convenience method that calls get_template_loader() on the DMP
    template engine instance.

    Note that while you can use this function to get a template loader object,
    the preferred method of rendering templates is through:
        1. dmp_render() and dmp_render_to_string().  See the DMP tutorial
           for information about these methods.
        2. Django's standard render() shortcut function.
    '''
    return get_dmp_instance().get_template_loader(app, subdir)


def get_template_loader_for_path(path, use_cache=True):
    '''
    Convenience method that calls get_template_loader_for_path() on the DMP
    template engine instance.

    Note that while you can use this function to get a template loader object,
    the preferred method of rendering templates is through:
        1. dmp_render() and dmp_render_to_string().  See the DMP tutorial
           for information about these methods.
        2. Django's standard render() shortcut function.
    '''
    return get_dmp_instance().get_template_loader_for_path(path, use_cache)


def get_template(app, template_name, subdir="templates", create=False):
    '''
    Convenience method that retrieves a template given the app and
    name of the template.

    Note that while you can use this function to get a template object,
    the preferred method of rendering templates is through:
        1. dmp_render() and dmp_render_to_string().  See the DMP tutorial
           for information about these methods.
        2. Django's standard render() shortcut function.
    '''
    return get_dmp_instance().get_template_loader(app, subdir, create=create).get_template(template_name)


def get_template_for_path(path, use_cache=True):
    '''
    Convenience method that retrieves a template given a direct path to it.

    Note that while you can use this function to get a template object,
    the preferred method of rendering templates is through:
        1. dmp_render() and dmp_render_to_string().  See the DMP tutorial
           for information about these methods.
        2. Django's standard render() shortcut function.
    '''
    app_path, template_name = os.path.split(path)
    return get_dmp_instance().get_template_loader_for_path(app_path, use_cache=use_cache).get_template(template_name)
