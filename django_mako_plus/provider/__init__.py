from django.apps import apps
from django.template import Context

import mako.runtime

from .runner import ProviderRun
from ..util import get_dmp_instance

import io



#########################################################
###  Primary functions

def links(tself, version_id=None, group=None):
    '''Returns the HTML for the given provider group (or all groups if None)'''
    pr = ProviderRun(tself, version_id, group)
    pr.run()
    return pr.getvalue()


def template_links(request, app, template_name, context=None, version_id=None, group=None, force=True):
    '''
    Returns the HTML for the given provider group, using an app and template name.
    This method should not normally be used (use links() instead).  The use of
    this method is when provider need to be called from regular python code instead
    of from within a rendering template environment.
    '''
    if isinstance(app, str):
        app = apps.get_app_config(app)
    if context is None:
        context = {}
    template_obj = get_dmp_instance().get_template_loader(app, create=True).get_mako_template(template_name, force=force)
    return template_obj_links(request, template_obj, context, version_id, group)


def template_obj_links(request, template_obj, context=None, version_id=None, group=None):
    '''
    Returns the HTML for the given provider group, using a template object.
    This method should not normally be used (use links() instead).  The use of
    this method is when provider need to be called from regular python code instead
    of from within a rendering template environment.
    '''
    # the template_obj can be a MakoTemplateAdapter or a Mako Template
    # if our DMP-defined MakoTemplateAdapter, switch to the embedded Mako Template
    template_obj = getattr(template_obj, 'mako_template', template_obj)
    # create a mako context so it seems like we are inside a render
    context_dict = {
        'request': request,
    }
    if isinstance(context, Context):
        for d in context:
            context_dict.update(d)
    elif context is not None:
        context_dict.update(context)
    mako_context = create_mako_context(template_obj, **context_dict)
    return links(mako_context['self'], version_id=version_id, group=group)


def create_mako_context(template_obj, **kwargs):
    # I'm hacking into private Mako methods here, but I can't see another
    # way to do this.  Hopefully this can be rectified at some point.
    kwargs.pop('self', None)  # some contexts have self in them, and it messes up render_unicode below because we get two selfs
    runtime_context = mako.runtime.Context(io.BytesIO(), **kwargs)
    runtime_context._set_with_template(template_obj)
    _, mako_context = mako.runtime._populate_self_namespace(runtime_context, template_obj)
    return mako_context
