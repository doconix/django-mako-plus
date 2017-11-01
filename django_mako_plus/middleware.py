from django.core.exceptions import ImproperlyConfigured
from urllib.parse import unquote

# try to import MiddlewareMixIn (Django 1.10+)
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # create a dummy MiddlewareMixin if older Django
    MiddlewareMixin = object

from .registry import is_dmp_app
from .router import ClassBasedRouter, get_router
from .util import DMP_OPTIONS, URLParamList, log
from .template import render_to_response_shortcut, render_to_string_shortcut

import logging

##########################################################
###   Middleware the prepares the request for
###   use with the controller.

DMP_PARAM_CHECK = ( 'dmp_router_app', 'dmp_router_page', 'dmp_router_function', 'urlparams' )

def default_render(*args, **kwargs):
    '''This function is set as the initial render function (below) until process_view sets the app-specific one (also below)'''
    raise ImproperlyConfigured(
        "DMP's app-specific render functions were not placed on the request object. "
        "This app is 1) not a DMP-enabled app or 2) rendering was done before the middleware's process_view() method was called. "
        "Fix the middleware issue, or if this instance needs to render without dependence on middleware, use DMP's render_template() convenience method instead. "
    )


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
        request.urlparams = URLParamList()
        request.dmp_render = default_render
        request.dmp_render_to_response = default_render
        request._dmp_router_callable = None


    def process_view(self, request, view_func, view_args, view_kwargs):
        '''
        Adds the following to the request object:

            request.dmp_router_app        The Django application (such as "homepage"), as a string.
            request.dmp_router_page       The view module (such as "index" for index.py), as a string.
            request.dmp_router_function   The function within the view module to be called (usually "process_request"), as a string.
            request.dmp_router_module     The module path in Python terms (such as homepage.views.index), as a string.
            request.dmp_router_class      This is set to None in this method, but route_request() fills it in, as a string, if a class-based view.
            request.urlparams             A list of the remaining url parts, as a list of strings.  See the tutorial for more information on this parameter.
            request._dmp_router_callable   The view callable (function, method, etc.) to be called by the router.

        Named parameters in the url pattern determines the values of these variables.
        See django_mako_plus/urls.py for the DMP standard patterns.  For example, one pattern
        specifies the router app, page, function, and urlparams: /app/page.function/urlparams

            ^(?P<dmp_router_app>[_a-zA-Z0-9\-]+)/(?P<dmp_router_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_router_function>[_a-zA-Z0-9\.\-]+)/?(?P<urlparams>.*)$

        As view middleware, this function runs just before the router.route_request is called.
        '''
        # set a flag on the request to check for double runs (middleware listed twice in settings)
        # double runs don't work because we pop off the kwargs below
        if hasattr(request, '_dmp_router_middleware_flag'):
            raise ImproperlyConfigured(
                "The Django Mako Plus middleware is running twice on this request."
                "Please check settings.py to see it the middleware might be listed twice."
            )
        request._dmp_router_middleware_flag = True

        # print debug messages to help with urls.py regex issues
        if log.isEnabledFor(logging.DEBUG):
            kwarg_params = [ param for param in DMP_PARAM_CHECK if param in view_kwargs ]
            missing_params = [ param for param in DMP_PARAM_CHECK if param not in view_kwargs ]
            log.debug('variables set by urls.py: %s; variables set by defaults: %s', kwarg_params, missing_params)

        # add the variables to the request
        request.dmp_router_app = view_kwargs.pop('dmp_router_app', None) or DMP_OPTIONS.get('DEFAULT_APP', 'homepage')
        if is_dmp_app(request.dmp_router_app):
            request.dmp_render = render_to_response_shortcut(request.dmp_router_app, request)
            request.dmp_render_to_string = render_to_string_shortcut(request.dmp_router_app, request)
        request.dmp_router_page = view_kwargs.pop('dmp_router_page', None) or DMP_OPTIONS.get('DEFAULT_PAGE', 'index')
        request.dmp_router_function = view_kwargs.pop('dmp_router_function', None)
        if request.dmp_router_function:
            fallback_template = '{}.{}.html'.format(request.dmp_router_page, request.dmp_router_function)
        else:
            fallback_template = '{}.html'.format(request.dmp_router_page)
            request.dmp_router_function = 'process_request'

        # period and dash cannot be in python names, but we allow dash in app, dash in page, and dash/period in function
        request.dmp_router_app = request.dmp_router_app.replace('-', '_')
        request.dmp_router_page = request.dmp_router_page.replace('-', '_')
        request.dmp_router_function = request.dmp_router_function.replace('.', '_').replace('-', '_')

        # add the full module path to the request
        request.dmp_router_module = '.'.join([ request.dmp_router_app, 'views', request.dmp_router_page ])

        # add the url parameters to the request
        # note that I'm not using unquote_plus because the + switches to a space *after* the question mark (in the regular parameters)
        # in the normal url, spaces should be quoted with %20.  Thanks Rosie for the tip.
        kwarg_urlparams = view_kwargs.pop('urlparams', '').strip()
        if kwarg_urlparams:
            request.urlparams.extend(( unquote(s) for s in kwarg_urlparams.split('/') ))

        # get the function object - the return of get_router_function might be a function, a class-based view, or a template
        # get_router_function does some magic to make all of these act like a regular view function
        request._dmp_router_callable = get_router(request.dmp_router_module, request.dmp_router_function, request.dmp_router_app, fallback_template)

        # adjust the variable values if a class
        if isinstance(request._dmp_router_callable, ClassBasedRouter):
            request.dmp_router_class = request.dmp_router_function
            request.dmp_router_function = request.method.lower()
            
        # debugging
        # for attr in (
        #     'dmp_router_app',
        #     'dmp_router_page',
        #     'dmp_router_function',
        #     'dmp_router_module',
        #     'dmp_router_class',
        #     'urlparams',
        #     'dmp_render',
        #     'dmp_render_to_string',
        #     '_dmp_router_callable',
        # ):
        #     print('{:30} {}'.format('request.' + attr + ':', getattr(request, attr)))
