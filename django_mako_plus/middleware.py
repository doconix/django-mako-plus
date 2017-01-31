from django.core.exceptions import ImproperlyConfigured
from django.views.generic import View
from urllib.parse import unquote

# try to import MiddlewareMixIn (Django 1.10+)
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # create a dummy MiddlewareMixin if older Django
    MiddlewareMixin = object

from .router import route_request
from .util import URLParamList, get_dmp_instance, DMP_OPTIONS, log
from .util import DMP_VIEW_CLASS_METHOD

import logging

##########################################################
###   Middleware the prepares the request for
###   use with the controller.

EMPTY_URLPARAMS = URLParamList()


class RequestInitMiddleware(MiddlewareMixin):
    '''
    Adds several fields to the request that our controller needs.
    Projects can customize the variables with view middleware that runs after this class.

    This class must be included in settings.py -> MIDDLEWARE.
    '''

    def process_request(self, request):
        '''
        Adds stubs for the DMP custom variables to the request object.

        We do this early in the middleware process because process_view() below gets called
        *after* URL resolution.  If an exception occurs before that (a 404, a middleware exception),
        the variables won't be put on the request object.  Therefore, we put stubs on it at the
        earliest possible place so they exist even if we don't get to process_view().
        '''
        request.dmp_router_app = None
        request.dmp_router_page = None
        request.dmp_router_function = None
        request.dmp_router_module = None
        request.dmp_router_class = None
        request.urlparams = EMPTY_URLPARAMS
        request.dmp_router_callback = None


    def process_view(self, request, view_func, view_args, view_kwargs):
        '''
        Adds the following to the request object:

            request.dmp_router_app        The Django application (such as "homepage"), as a string.
            request.dmp_router_page       The view module (such as "index" for index.py), as a string.
            request.dmp_router_function   The function within the view module to be called (usually "process_request"), as a string.
            request.dmp_router_module     The module path in Python terms (such as homepage.views.index), as a string.
            request.dmp_router_class      This is set to None in this method, but route_request() fills it in, as a string, if a class-based view.
            request.urlparams             A list of the remaining url parts, as a list of strings.  See the tutorial for more information on this parameter.
            request.dmp_router_callback   The view callable (function, method, etc.) to be called by the router.

        Named parameters in the url pattern determines the values of these variables.
        See django_mako_plus/urls.py for the DMP standard patterns.  For example, one pattern
        specifies the router app, page, function, and urlparams: /app/page.function/urlparams

            ^(?P<dmp_router_app>[_a-zA-Z0-9\-]+)/(?P<dmp_router_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_router_function>[_a-zA-Z0-9\.\-]+)/?(?P<urlparams>.*)$

        As view middleware, this function runs just before the router.route_request is called.
        '''
        # print debug messages to help with urls.py regex issues
        if log.isEnabledFor(logging.DEBUG):
            if view_func is not route_request:
                log.debug("DMP is not handling this request because the matched urls.py regex did not resolve to route_request. The request.dmp_* variables will not be set.")
            else:
                for param in ( 'dmp_router_app', 'dmp_router_page', 'dmp_router_function', 'urlparams' ):
                    if param not in view_kwargs:
                        log.debug('The matched urls.py regex did not contain the named parameter "{}"; using the default value from settings.py.'.format(param))

        # if urls.py didn't resolve to DMP, we don't need to set any of these variables
        if view_func is not route_request:
            return

        # add the variables to the request
        request.dmp_router_app = view_kwargs.pop('dmp_router_app', None) or DMP_OPTIONS.get('DEFAULT_APP', 'homepage')
        request.dmp_router_page = view_kwargs.pop('dmp_router_page', None) or DMP_OPTIONS.get('DEFAULT_PAGE', 'index')
        request.dmp_router_function = view_kwargs.pop('dmp_router_function', None)
        if request.dmp_router_function:
            request.dmp_router_fallback = '{}.{}.html'.format(request.dmp_router_page, request.dmp_router_function)
        else:
            request.dmp_router_fallback = '{}.html'.format(request.dmp_router_page)
            request.dmp_router_function = 'process_request'

        # period and dash cannot be in python names, but we allow dash in app and page and (dash or period) in the function
        # these change into underscores
        request.dmp_router_app = request.dmp_router_app.replace('-', '_')
        request.dmp_router_page = request.dmp_router_page.replace('-', '_')
        request.dmp_router_function = request.dmp_router_function.replace('.', '_').replace('-', '_')

        # add the full module path to the request
        request.dmp_router_module = '.'.join([ request.dmp_router_app, 'views', request.dmp_router_page ])

        # add the url parameters to the request
        # note that I'm not using unquote_plus because the + switches to a space *after* the question mark (in the regular parameters)
        # in the normal url, spaces should be quoted with %20.  Thanks Rosie for the tip.
        request.urlparams = URLParamList(( unquote(s) for s in view_kwargs.pop('urlparams', '').split('/') ))

        # get the function object - the return of get_view_function might be a function, a class-based view, or a template
        # get_view_function does some magic to make all of these act like a regular view function
        request.dmp_router_callback = get_dmp_instance().get_view_function(request.dmp_router_app, request.dmp_router_module, request.dmp_router_function, request.dmp_router_fallback)

        # adjust the variable values if a class
        if request.dmp_router_callback._dmp_view_type == DMP_VIEW_CLASS_METHOD:
            request.dmp_router_class = request.dmp_router_function
            request.dmp_router_function = request.method.lower()
        # debugging
        # print('request.dmp_router_app        ', request.dmp_router_app        )
        # print('request.dmp_router_page       ', request.dmp_router_page       )
        # print('request.dmp_router_function   ', request.dmp_router_function   )
        # print('request.dmp_router_module     ', request.dmp_router_module     )
        # print('request.dmp_router_class      ', request.dmp_router_class      )
        # print('request.urlparams             ', request.urlparams             )
        # print('request.dmp_router_callback   ', request.dmp_router_callback   )
