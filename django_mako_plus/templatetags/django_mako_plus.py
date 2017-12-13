from django import template
from django.utils.safestring import mark_safe
from ..convenience import render_template

register = template.Library()

@register.simple_tag(takes_context=True)
def dmp_include(context, app, template_name, def_name=None):
    '''Standard Django tag to include a DMP (mako) template.'''
    return mark_safe(render_template(
        request=context.get('request'), 
        app=app, 
        template_name=template_name, 
        context=context.flatten(), 
        def_name=def_name
    ))
