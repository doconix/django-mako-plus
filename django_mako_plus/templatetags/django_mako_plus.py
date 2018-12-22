from django import template
from django.utils.safestring import mark_safe
from ..convenience import render_template

register = template.Library()

###########################################
###  The tags in this file are DJANGO
###  tags, not Mako ones.

@register.simple_tag(takes_context=True)
def dmp_include(context, app, template_name, def_name=None):
    '''
    Includes a DMP (Mako) template into a normal django template.

    In other words, this is used whenyou have a Django-style template and
    need to include another template within it -- but that template is written
    in DMP (Mako) syntax rather than Django syntax.
    '''
    return mark_safe(render_template(
        request=context.get('request'),
        app=app,
        template_name=template_name,
        context=context.flatten(),
        def_name=def_name
    ))
