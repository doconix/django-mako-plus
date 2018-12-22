from mako.runtime import supports_caller

###
###  Mako-style tags that DMP provides
###


#########################################################
###  Autoescaping toggling

# attaching to `caller_stack` because it's the same object
# throughout rendering of a template inheritance
AUTOESCAPE_KEY = '__dmp_autoescape'

def is_autoescape(context):
    return bool(getattr(context.caller_stack, AUTOESCAPE_KEY, True))

def toggle_autoescape(context, escape_on=True):
    previous = is_autoescape(context)
    setattr(context.caller_stack, AUTOESCAPE_KEY, escape_on)
    try:
        context['caller'].body()
    finally:
        setattr(context.caller_stack, AUTOESCAPE_KEY, previous)


@supports_caller
def autoescape_on(context):
    '''
    Explicitly turns autoescaping on for a given block within a template,
    (individual filters can still override with ${ somevar | n }).

    Example use in template:
        <%namespace name="dmp" module="django_mako_plus.tags"/>

        <%dmp:autoescape_on>
            ${ somevar } will be autoescaped.
        </%dmp:autoescape_on>
    '''
    toggle_autoescape(context, True)
    return ''


@supports_caller
def autoescape_off(context):
    '''
    Explicitly turns autoescaping off for a given block within a template,
    (individual filters can still override with ${ somevar | h }).

    Example use in template:
        <%namespace name="dmp" module="django_mako_plus.tags"/>

        <%dmp:autoescape>
            ${ somevar } will not be autoescaped.
        </%dmp:autoescape>
    '''
    toggle_autoescape(context, False)
    return ''
