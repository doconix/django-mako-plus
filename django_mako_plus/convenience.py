from .util import get_dmp_instance


##############################################################
###   Convenience functions that exist in the DMP module
###   These are imported into __init__.py

def get_template_loader(app, subdir='templates', create=False):
    '''
    Convenience method that calls get_template_loader() on the DMP
    template engine instance.

    See the documentation of MakoTemplates.get_template_loader() for
    information about this method.
    '''
    return get_dmp_instance().get_template_loader(app, subdir)


def get_template_loader_for_path(path, use_cache=True):
    '''
    Convenience method that calls get_template_loader_for_path() on the DMP
    template engine instance.

    See the documentation of MakoTemplates.get_template_loader_for_path() for
    information about this method.
    '''
    return get_dmp_instance().get_template_loader_for_path(path, use_cache)
