from django import template
from django.apps import apps
from django.utils.safestring import mark_safe


###############################################################
###  DJANGO template tag to include a Mako template
###
###  This file is called "django_mako_plus.py" because it's
###  the convention for creating Django template tags.
###
###  See also django_mako_plus/filters.py

register = template.Library()

@register.simple_tag(takes_context=True)
def dmp_include(context, template_name, def_name=None, **kwargs):
    '''
    Includes a DMP (Mako) template into a normal django template.

    context:        automatically provided
    template_name:  specified as "app/template"
    def_name:       optional block to render within the template

    Example:
        {% load django_mako_plus %}
        {% dmp_include "homepage/bsnav_dj.html" %}
        or
        {% dmp_include "homepage/bsnav_dj.html" "blockname" %}
    '''
    dmp = apps.get_app_config('django_mako_plus')
    template = dmp.engine.get_template(template_name)
    dmpcontext = context.flatten()
    dmpcontext.update(kwargs)
    return mark_safe(template.render(
        context=dmpcontext,
        request=context.get('request'),
        def_name=def_name
    ))
