from django.conf import settings
from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured, ViewDoesNotExist
from django.http import HttpResponse, StreamingHttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.template import TemplateDoesNotExist, TemplateSyntaxError

from .exceptions import InternalRedirectException, RedirectException, DMPViewDoesNotExist
from .signals import dmp_signal_pre_process_request, dmp_signal_post_process_request, dmp_signal_internal_redirect_exception, dmp_signal_redirect_exception
from .template import TemplateViewFunction
from .util import get_dmp_instance, get_dmp_app_configs, log, DMP_OPTIONS
from .util import DMP_VIEW_ERROR, DMP_VIEW_FUNCTION, DMP_VIEW_CLASS_METHOD, DMP_VIEW_TEMPLATE

import os, os.path, re, mimetypes, sys, logging, pkgutil
from urllib.parse import unquote
from importlib import import_module



##############################################################
###   The front controller of all views on the site.
###   urls.py routes everything through this method.

def route_request(request, *args, **kwargs):
    '''
    The main router for all calls coming in to the system.  Patterns in urls.py should call this function.
    '''
    # wrap to enable the InternalRedirectExceptions to loop around
    response = None
    while True:
        # an outer try that catches the redirect exceptions
        try:
            # output the variables so the programmer can debug where this is routing
            if log.isEnabledFor(logging.INFO):
                log.info('processing: app={}, page={}, module={}, func={}, urlparams={}'.format(request.dmp_router_app, request.dmp_router_page, request.dmp_router_module, request.dmp_router_function, request.urlparams))

            # ensure we have a dmp_router_callback variable on request
            if getattr(request, 'dmp_router_callback', None) is None:
                raise ImproperlyConfigured("Variable request.dmp_router_callback does not exist (check MIDDLEWARE for `django_mako_plus.RequestInitMiddleware`).")

            # if we had a view not found, raise a 404
            if isinstance(request.dmp_router_callback, ViewDoesNotExist) or request.dmp_router_callback._dmp_view_type is DMP_VIEW_ERROR:
                log.error(str(request.dmp_router_callback))
                raise Http404

            # send the pre-signal
            if DMP_OPTIONS.get('SIGNALS', False):
                for receiver, ret_response in dmp_signal_pre_process_request.send(sender=sys.modules[__name__], request=request):
                    if isinstance(ret_response, (HttpResponse, StreamingHttpResponse)):
                        return ret_response

            # log the view
            if log.isEnabledFor(logging.INFO):
                if request.dmp_router_callback._dmp_view_type is DMP_VIEW_CLASS_METHOD:
                    log.info('calling class-based view function {}.{}.{}'.format(request.dmp_router_module, request.dmp_router_class, request.dmp_router_function))
                elif request.dmp_router_callback._dmp_view_type is DMP_VIEW_TEMPLATE:
                    log.info('view function {}.{} not found; rendering template {}'.format(request.dmp_router_module, request.dmp_router_function, request.dmp_router_fallback))
                else: # assume a view function
                    log.info('calling view function {}.{}'.format(request.dmp_router_module, request.dmp_router_function))

            # call view function with any args and any remaining kwargs
            response = request.dmp_router_callback(request, *args, **kwargs)

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
            # resolve to a function
            request.dmp_router_module = ivr.redirect_module
            request.dmp_router_function = ivr.redirect_function
            try:
                module_obj = import_module(request.dmp_router_module)
                request.dmp_router_callback = getattr(module_obj, request.dmp_router_function, None)
                if request.dmp_router_callback == None:
                    request.dmp_router_callback = DMPViewDoesNotExist('Module {} found successfully during internal redirect, but view function {} is not defined in the module.'.format(request.dmp_router_module, request.dmp_router_function))
            except ImportError:
                request.dmp_router_callback = DMPViewDoesNotExist('View function {}.{} not found during internal redirect.'.format(request.dmp_router_module, request.dmp_router_function))
            # do the internal redirect
            log.info('received an InternalViewRedirect to {} -> {}'.format(request.dmp_router_module, request.dmp_router_function))

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
    raise Exception("Django-Mako-Plus error: The route_request() function should not have been able to get to this point.  Please notify the owner of the DMP project.  Thanks.")





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
    f._dmp_view_type = DMP_VIEW_FUNCTION
    return f



