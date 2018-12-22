from django.apps import apps
from django.template import Context
from django.utils.safestring import mark_safe

from .runner import ProviderRun
from ..template import create_mako_context

import io



#########################################################
###  Primary functions

def links(tself, version_id=None, group=None):
    '''Returns the HTML for the given provider group (or all groups if None)'''
    pr = ProviderRun(tself, version_id, group)
    pr.run()
    return mark_safe(pr.getvalue())


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
    dmp = apps.get_app_config('django_mako_plus')
    template_obj = dmp.engine.get_template_loader(app, create=True).get_mako_template(template_name, force=force)
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
