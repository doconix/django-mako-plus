from django.conf import settings
from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured, ViewDoesNotExist
from django.http import HttpResponse, StreamingHttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.template import TemplateDoesNotExist, TemplateSyntaxError

from .exceptions import InternalRedirectException, RedirectException
from .signals import dmp_signal_pre_process_request, dmp_signal_post_process_request, dmp_signal_internal_redirect_exception, dmp_signal_redirect_exception
from .util import get_dmp_instance, get_dmp_app_configs, log, DMP_OPTIONS
from .util import DMP_VIEW_ERROR, DMP_VIEW_FUNCTION, DMP_VIEW_CLASS, DMP_VIEW_TEMPLATE
from .util import URLParamList

import os, os.path, re, mimetypes, sys, logging, pkgutil
from urllib.parse import unquote
from importlib import import_module



##############################################################
###   The front controller of all views on the site.
###   urls.py routes everything through this method.

def route_request(request, *args, **kwargs):
    '''The main router for all calls coming in to the system.'''
    engine = get_dmp_instance()

    # add the url parts to the url
    parse_path(request, kwargs)

    # first try going to the view function for this request
    # we look for a views/name.py file where name is the same name as the HTML file
    response = None

    while True: # enables the InternalRedirectExceptions to loop around
        # an outer try that catches the redirect exceptions
        try:

            # get the function object - the return of get_view_function might be a function, a class-based view, or a template
            # get_view_function does some magic to make all of these act like a regular view function
            try:
                func_obj, func_type = engine.get_view_function(request.dmp_router_app, request.dmp_router_module, request.dmp_router_function, request.dmp_router_page_full + '.html')
            except ViewDoesNotExist as e:
                log.error(str(e))
                raise Http404

            # adjust the request fields for special function types
            if func_type == DMP_VIEW_CLASS:
                request.dmp_router_class = request.dmp_router_function
                request.dmp_router_function = request.method.lower()

            # output the variables so the programmer can debug where this is routing
            if log.isEnabledFor(logging.INFO):
                log.info('processing: app={}, page={}, func={}, urlparams={}'.format(request.dmp_router_app, request.dmp_router_page, request.dmp_router_function, request.urlparams))

            # send the pre-signal
            if DMP_OPTIONS.get('SIGNALS', False):
                for receiver, ret_response in dmp_signal_pre_process_request.send(sender=sys.modules[__name__], request=request):
                    if isinstance(ret_response, (HttpResponse, StreamingHttpResponse)):
                        return ret_response

            # call view function
            if log.isEnabledFor(logging.INFO):
                if func_type == DMP_VIEW_FUNCTION:
                    log.info('calling view function {}.{}'.format(request.dmp_router_module, request.dmp_router_function))
                elif func_type == DMP_VIEW_CLASS:
                    log.info('calling class-based view function {}.{}.{}'.format(request.dmp_router_module, request.dmp_router_class, request.dmp_router_function))
                elif func_type == DMP_VIEW_TEMPLATE:
                    log.info('view function {}.{} not found; rendering template {}'.format(request.dmp_router_module, request.dmp_router_function, request.dmp_router_page_full + '.html'))
            response = func_obj(request)

            # send the post-signal
            if DMP_OPTIONS.get('SIGNALS', False):
                for receiver, ret_response in dmp_signal_post_process_request.send(sender=sys.modules[__name__], request=request, response=response):
                    if ret_response != None:
                        response = ret_response # sets it to the last non-None in the signal receiver chain

            # if we didn't get a correct response back, send a 404
            if not isinstance(response, (HttpResponse, StreamingHttpResponse)):
                if request.dmp_router_class == None:
                    log.error('view function {}.{} failed to return an HttpResponse (or the post-signal overwrote it).  Returning Http404.'.format(request.dmp_router_module, request.dmp_router_function))
                else:
                    log.error('class-based view function {}.{}.{} failed to return an HttpResponse (or the post-signal overwrote it).  Returning Http404.'.format(request.dmp_router_module, request.dmp_router_class, request.dmp_router_function))
                raise Http404

            # return the response
            return response

        except InternalRedirectException as ivr:
            # send the signal
            if DMP_OPTIONS.get('SIGNALS', False):
                dmp_signal_internal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=ivr)
            # do the internal redirect
            request.dmp_router_module = ivr.redirect_module
            request.dmp_router_function = ivr.redirect_function
            full_module_filename = os.path.normpath(os.path.join(settings.BASE_DIR, request.dmp_router_module.replace('.', '/') + '.py'))
            log.info('received an InternalViewRedirect to {} -> {}'.format(full_module_filename, request.dmp_router_function))

        except RedirectException as e: # redirect to another page
            if request.dmp_router_class == None:
                log.info('view function {}.{} redirected processing to {}'.format(request.dmp_router_module, request.dmp_router_function, e.redirect_to))
            else:
                log.info('class-based view function {}.{}.{} redirected processing to {}'.format(request.dmp_router_module, request.dmp_router_class, request.dmp_router_function, e.redirect_to))
            # send the signal
            if DMP_OPTIONS.get('SIGNALS', False):
                dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
            # send the browser the redirect command
            return e.get_response(request)

    # the code should never get here
    raise Exception("Django-Mako-Plus router error: The route_request() function should not have been able to get to this point.  Please notify the owner of the DMP project.  Thanks.")





###############################################################
###   A decorator that signals that a function is callable
###   by DMP.  This prevents "just any function" from being
###   called by the router above.
###

def view_function(f):
    '''
    A decorator to signify which view functions are "callable" by web browsers.

    Any endpoint function, such as process_request, must be decorated to be callable:

        @view_function
        function process_request(request):
            ...

    The @view_function decorator must be the first one listed if other decorators are present.
    Note that class-based views don't need to be decorated because we allow anything that extends Django's View class.
    '''
    # This decorator is more of an annotation on functions than a decorator.
    # Rather than the usual inner function pattern, I'm simply setting a flag on the
    # function to signify that it is callable.  The router checks this flag
    # before calling the function.
    f._dmp_view_function = True
    return f




################################################################
###   Helper functions

RE_DMP_FUNCTION = re.compile('^([^\.]*)\.(.*)$')

def parse_path(request, kwargs):
    '''
    Called by route_request() above.  Adds the following to the request object:

        request.dmp_router_app        The Django application (such as "calculator").
        request.dmp_router_page       The view module (such as "calc" for calc.py).
        request.dmp_router_page_full  The view module as specified in the URL, including the function name if specified.
        request.dmp_router_function   The function within the view module to be called (usually "process_request").
        request.dmp_router_module     The module path in Python terms, such as calculator.views.calc.
        request.dmp_router_class      This is set to None in this method, but route_request() fills it in if a class-based view.
        request.urlparams             A list of the remaining url parts (see the calc.py example).

    In each case, it first tries to get the parameter from the kwargs.  The items will be in kwargs
    when a urls.py pattern contains these names.
    '''
    # app and page
    request.dmp_router_app = kwargs.pop('dmp_router_app', None)
    request.dmp_router_page = request.dmp_router_page_full = kwargs.pop('dmp_router_page', None)

    # function, parsing from dmp_router_page if the url regex didn't name it
    request.dmp_router_function = kwargs.pop('dmp_router_function', None)
    if request.dmp_router_function is None:
        match = RE_DMP_FUNCTION.search(request.dmp_router_page)
        if match:
            request.dmp_router_page = match.group(1)
            request.dmp_router_function = match.group(2)
        else:
            request.dmp_router_function = 'process_request'

    # create the full module path
    request.dmp_router_module = '.'.join([ request.dmp_router_app, 'views', request.dmp_router_page ])

    # set the class to be None (set in route_request() if a class-based view)
    request.dmp_router_class = None

    # set up the urlparams with the reamining path parts
    # note that I'm not using unquote_plus because the + switches to a space *after* the question mark (in the regular parameters)
    # in the normal url, spaces have to be quoted with %20.  Thanks Rosie for the tip.
    request.urlparams = URLParamList(( unquote(s) for s in kwargs.pop('urlparams', '').split('/') ))

    print('request.dmp_router_app       ', request.dmp_router_app       )
    print('request.dmp_router_page      ', request.dmp_router_page      )
    print('request.dmp_router_page_full ', request.dmp_router_page_full )
    print('request.dmp_router_function  ', request.dmp_router_function  )
    print('request.dmp_router_module    ', request.dmp_router_module    )
    print('request.dmp_router_class     ', request.dmp_router_class     )
    print('request.urlparams            ', request.urlparams            )



