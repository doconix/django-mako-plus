from django.template import engines
from django.template import TemplateDoesNotExist
from mako.runtime import supports_caller

###
###  Mako-style tags that DMP provides
###


###############################################################
###  Include Django templates
###

def django_include(context, template_name, **kwargs):
    '''
    Mako tag to include a Django template withing the current DMP (Mako) template.
    Since this is a Django template, it is search for using the Django search
    algorithm (instead of the DMP app-based concept).
    See https://docs.djangoproject.com/en/2.1/topics/templates/.

    The current context is sent to the included template, which makes all context
    variables available to the Django template. Any additional kwargs are added
    to the context.
    '''
    try:
        djengine = engines['django']
    except KeyError as e:
        raise TemplateDoesNotExist("Django template engine not configured in settings, so template cannot be found: {}".format(template_name)) from e
    djtemplate = djengine.get_template(template_name)
    djcontext = {}
    djcontext.update(context)
    djcontext.update(kwargs)
    return djtemplate.render(djcontext, context['request'])



#########################################################
###  Template autoescaping on/off

# attaching to `caller_stack` because it's the same object
# throughout rendering of a template inheritance
AUTOESCAPE_KEY = '__dmp_autoescape'

def is_autoescape(context):
    return bool(getattr(context.caller_stack, AUTOESCAPE_KEY, True))


def _toggle_autoescape(context, escape_on=True):
    '''
    Internal method to toggle autoescaping on or off. This function
    needs access to the caller, so the calling method must be
    decorated with @supports_caller.
    '''
    previous = is_autoescape(context)
    setattr(context.caller_stack, AUTOESCAPE_KEY, escape_on)
    try:
        context['caller'].body()
    finally:
        setattr(context.caller_stack, AUTOESCAPE_KEY, previous)


@supports_caller
def autoescape_on(context):
    '''
    Mako tag to enable autoescaping for a given block within a template,
    (individual filters can still override with ${ somevar | n }).

    Example:
        <%namespace name="dmp" module="django_mako_plus.tags"/>
        <%dmp:autoescape_on>
            ${ somevar } will be autoescaped.
        </%dmp:autoescape_on>
    '''
    _toggle_autoescape(context, True)
    return ''


@supports_caller
def autoescape_off(context):
    '''
    Mako tag to disable autoescaping for a given block within a template,
    (individual filters can still override with ${ somevar | h }).

    Example:
        <%namespace name="dmp" module="django_mako_plus.tags"/>
        <%dmp:autoescape>
            ${ somevar } will not be autoescaped.
        </%dmp:autoescape>
    '''
    _toggle_autoescape(context, False)
    return ''
