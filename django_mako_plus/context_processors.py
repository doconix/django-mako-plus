################################################################
###   A set of request processors that add variables to the
###   context (parameters) when templates are rendered.
###

from django.conf import settings as conf_settings


def settings(request):
    '''Adds the settings dictionary to the request'''
    return { 'settings': conf_settings }
