from django.core.exceptions import ImproperlyConfigured
from urllib.parse import unquote

# try to import MiddlewareMixIn (Django 1.10+)
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # create a dummy MiddlewareMixin if older Django
    MiddlewareMixin = object

from .util import URLParamList, get_dmp_instance, DMP_OPTIONS


##########################################################
###   Middleware the prepares the request for
###   use with the controller.

class RequestInitMiddleware(MiddlewareMixin):
    '''
    Adds several fields to the request that our controller needs.
    Projects can customize the variables with view middleware that runs after this class.

    This class must be included in settings.py -> MIDDLEWARE.
    '''

    def process_view(self, request, view_func, view_args, view_kwargs):
        '''
        Adds the following to the request object:

            request.dmp_router_app        The Django application (such as "homepage"), as a string.
            request.dmp_router_page       The view module (such as "index" for index.py), as a string.
            request.dmp_router_function   The function within the view module to be called (usually "process_request"), as a string.
            request.dmp_router_module     The module path in Python terms (such as homepage.views.index), as a string.
            request.dmp_router_fallback   The fallback template name if the view does not exist, as a string.
            request.dmp_router_class      This is set to None in this method, but route_request() fills it in, as a string, if a class-based view.
            request.urlparams             A list of the remaining url parts, as a list of strings.  See the tutorial for more information on this parameter.

        Named parameters in the url pattern determines the values of these variables.
        See django_mako_plus/urls.py for the DMP standard patterns.  For example, one pattern
        specifies the router app, page, function, and urlparams: /app/page.function/urlparams

            ^(?P<dmp_router_app>[_a-zA-Z0-9]+)/(?P<dmp_router_page>[_a-zA-Z0-9]+)\.(?P<dmp_router_function>[_a-zA-Z0-9]+)/?(?P<urlparams>.*)$

        As view middleware, this function runs just before the router.route_request is called.
        '''
        # add the variables to the request
        request.dmp_router_app = view_kwargs.pop('dmp_router_app', None) or DMP_OPTIONS.get('DEFAULT_APP', 'homepage')
        request.dmp_router_page = view_kwargs.pop('dmp_router_page', None) or DMP_OPTIONS.get('DEFAULT_PAGE', 'index')
        request.dmp_router_function = view_kwargs.pop('dmp_router_function', None)
        if request.dmp_router_function:
            request.dmp_router_fallback = '{}.{}.html'.format(request.dmp_router_page, request.dmp_router_function)
        else:
            request.dmp_router_fallback = '{}.html'.format(request.dmp_router_page)
            request.dmp_router_function = 'process_request'
        request.dmp_router_class = None  # this is set below if a class-based view

        # add the url parameters to the request
        # note that I'm not using unquote_plus because the + switches to a space *after* the question mark (in the regular parameters)
        # in the normal url, spaces should be quoted with %20.  Thanks Rosie for the tip.
        request.urlparams = URLParamList(( unquote(s) for s in view_kwargs.pop('urlparams', '').split('/') ))

        # add the full module path to the request
        request.dmp_router_module = '.'.join([ request.dmp_router_app, 'views', request.dmp_router_page ])


