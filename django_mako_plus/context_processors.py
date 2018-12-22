################################################################
###   A set of request processors that add variables to the
###   context (parameters) when templates are rendered.
###

from django.conf import settings as conf_settings
from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy



def settings(request):
    '''Adds the settings dictionary to the request'''
    return { 'settings': conf_settings }


def csrf(request):
    '''
    Adds the "csrf_input" and "csrf_token" variables to the request.

    Following Django's lead, this processor is included in DMP's
    default context processors list. It does not need to be listed
    in settings.py.

    To include the <input name="csrf".../> control in your forms,
    use ${ csrf_input }.
    '''
    return {
        'csrf_input': csrf_input_lazy(request),
        'csrf_token': csrf_token_lazy(request),
    }
