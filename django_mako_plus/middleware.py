from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
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
        request.dmp = DEFAULT_ROUTING_DATA


    def process_view(self, request, view_func, view_args, view_kwargs):
        '''
        Adds the following to the request object:

            request.dmp.app            The Django application (such as "homepage"), as a string.
            request.dmp.page           The view module (such as "index" for index.py), as a string.
            request.dmp.function       The function within the view module to be called (usually "process_request"),
                                       as a string.
            request.dmp.module         The module path in Python terms (such as homepage.views.index), as a string.
            request.dmp.class_obj      The class object, if a class-based view.
            request.dmp.function_obj   The view callable (function, method, etc.) to be called by the router.
            request.dmp.urlparams      A list of the remaining url parts, as a list of strings.
                                       View function parameter conversion uses the values in this list.

        As view middleware, this function runs just before the router.route_request is called.
        '''
        # ensure this hasn't run twice (such as having it in the middleware twice)
        if request.dmp is DEFAULT_ROUTING_DATA:
            return

        # create the RoutingData object
        request.dmp = RoutingData(
            view_kwargs.pop('dmp_router_app', None) or DMP_OPTIONS.get('DEFAULT_APP'),
            view_kwargs.pop('dmp_router_page', None) or DMP_OPTIONS.get('DEFAULT_PAGE', 'index'),
            view_kwargs.pop('dmp_router_function', None),
            view_kwargs.pop('urlparams', '').strip(),
        )
        print(request.dmp)

        # set the render methods on the request
        if is_dmp_app(request.dmp.app):
            request.render = render_to_response_shortcut(request.dmp.app, request)
            request.render_to_string = render_to_string_shortcut(request.dmp.app, request)
        else:
            request.render = default_render
            request.render_to_string = default_render


class RoutingData(object):
    '''
    The routing data for DMP.

    An default object is set at the beginning of the request.
    Then after the url pattern is matched, an object with the
    match data is created.
    '''
    def __init__(self, app, page, function, urlparams):
        '''These variables are set by the process_view method above'''
        # period and dash cannot be in python names, but we allow dash in app, dash in page, and dash/period in function
        self.app = app.replace('-', '_') if app is not None else None
        self.page = page.replace('-', '_') if page is not None else None
        if function:
            self.function = function.replace('.', '_').replace('-', '_')
            fallback_template = '{}.{}.html'.format(page, function)
        else:
            self.function = 'process_request'
            fallback_template = '{}.html'.format(page)

        # set the module and function
        # the return of get_router_function might be a function, a class-based view, or a template
        if self.app is not None and self.page is not None:
            self.module = '.'.join([ self.app, 'views', self.page ])
            self.class_obj = None
            self.function_obj = get_router(self.module, self.function, self.app, fallback_template)
            if isinstance(self.function_obj, ClassBasedRouter):
                self.class_obj = self.function_obj
                self.function = request.method.lower()
        else:
            self.module = None
            self.function_obj = None

        # adjust the variable values if a class

        # parse the urlparams
        # note that I'm not using unquote_plus because the + switches to a space *after* the question mark (in the regular parameters)
        # in the normal url, spaces should be quoted with %20.  Thanks Rosie for the tip.
        self.urlparams = URLParamList(( unquote(s) for s in urlparams.split('/') )) if urlparams else []


    def __repr__(self):
        '''Debugging information.'''
        return 'django_mako_plus RoutingData:' + \
            ''.join(('\n\t{:_<10}{}'.format(k, v) for k, v in (
                ( 'app', self.app ),
                ( 'page', self.page ),
                ( 'function', self.function ),
                ( 'module', self.module ),
                ( 'class_obj', self.class_obj ),
                ( 'function_obj', self.function_obj ),
                ( 'urlparams', self.urlparams ),
            )))



DEFAULT_ROUTING_DATA = RoutingData(None, None, None, None)
def default_render(*args, **kwargs):
    '''This function is set as the initial render function until process_view sets the app-specific one'''
    raise ImproperlyConfigured('''
DMP's app-specific render functions were not placed on the request object. Likely reasons:
    1) This app is not registered as a Django app (ensure the app is listed in `INSTALLED_APPS` in settings file).
    2) This app is not a DMP-enabled app (check for `DJANGO_MAKO_PLUS = True` in appdir/__init__.py).
    3) A template was rendered before the middleware's process_view() method was called (move after middleware call or use DMP's render_template() function which can be used anytime).
    '''.strip())

