from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, StreamingHttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.template import TemplateDoesNotExist, TemplateSyntaxError

from .exceptions import InternalRedirectException, RedirectException
from .signals import dmp_signal_pre_process_request, dmp_signal_post_process_request, dmp_signal_internal_redirect_exception, dmp_signal_redirect_exception
from .util import get_dmp_instance, log, DMP_OPTIONS

import os, os.path, re, mimetypes, sys, logging
from urllib.parse import unquote
from importlib import import_module





###############################################################
###   A decorator that signals that a function is callable
###   by DMP.  This prevents "just any function" from being
###   called by the router above.  The function must be
###   decorated to be callable:
###
###       @view_function
###       function process_request(request):
###           ...


def view_function(f):
    '''A decorator to signify which view functions are "callable" by web browsers.
       This decorator is more of an annotation on functions than a decorator.
       Rather than the usual inner function pattern, I'm simply setting a flag on the
       function to signify that it is callable.  The router checks this flag
       before calling the function.
    '''
    f.dmp_view_function = True
    return f





##############################################################
###   The front controller of all views on the site.
###   urls.py routes everything through this method.

def route_request(request):
    '''The main router for all calls coming in to the system.'''
    # output the variables so the programmer can debug where this is routing
    if log.isEnabledFor(logging.INFO):
        log.info('processing: app=%s, page=%s, func=%s, urlparams=%s' % (request.dmp_router_app, request.dmp_router_page, request.dmp_router_function, request.urlparams))

    # set the full function location
    request.dmp_router_module = '.'.join([ request.dmp_router_app, 'views', request.dmp_router_page ])

    # first try going to the view function for this request
    # we look for a views/name.py file where name is the same name as the HTML file
    response = None

    while True: # enables the InternalRedirectExceptions to loop around
        full_module_filename = os.path.normpath(os.path.join(settings.BASE_DIR, request.dmp_router_module.replace('.', '/') + '.py'))
        try:
            # look for the module, and if not found go straight to template
            if not os.path.exists(full_module_filename):
                log.warning('module %s not found; sending processing directly to template %s.html' % (request.dmp_router_module, request.dmp_router_page_full))
                try:
                    dmp_loader = get_dmp_instance().get_template_loader(request.dmp_router_app)
                    return dmp_loader.get_template('%s.html' % request.dmp_router_page_full).render_to_response(request=request)
                except (TemplateDoesNotExist, TemplateSyntaxError, ImproperlyConfigured) as e:
                    log.error('%s' % (e))
                    raise Http404

            # find the function
            module_obj = import_module(request.dmp_router_module)
            if not hasattr(module_obj, request.dmp_router_function):
                log.error('view function/class %s not in module %s; returning 404 not found.' % (request.dmp_router_function, request.dmp_router_module))
                raise Http404
            func_obj = getattr(module_obj, request.dmp_router_function)

            # see if the func_obj is actually a class -- we might be doing class-based views here
            if isinstance(func_obj, type):
                request.dmp_router_class = request.dmp_router_function
                request.dmp_router_function = request.method.lower()
                if not hasattr(func_obj, request.dmp_router_function):
                    log.error('view class %s.%s has no method named %s; returning 404 not found.' % (request.dmp_router_module, request.dmp_router_class, request.dmp_router_function))
                    raise Http404
                func_obj = getattr(func_obj(), request.dmp_router_function)  # move to the class.get(), class.post(), etc. method

            # ensure it is decorated with @view_function - this is for security so only certain functions can be called
            if getattr(func_obj, 'dmp_view_function', False) != True:
                log.error('view function/class %s found successfully, but it is not decorated with @view_function; returning 404 not found.  Note that if you have multiple decorators on a function, the @view_function decorator must be listed first.' % (request.dmp_router_function))
                raise Http404

            # send the pre-signal
            if DMP_OPTIONS.get('SIGNALS', False):
                for receiver, ret_response in dmp_signal_pre_process_request.send(sender=sys.modules[__name__], request=request):
                    if isinstance(ret_response, (HttpResponse, StreamingHttpResponse)):
                        return ret_response

            # call view function
            if request.dmp_router_class == None and log.isEnabledFor(logging.INFO):
                log.info('calling view function %s.%s' % (request.dmp_router_module, request.dmp_router_function))
            elif log.isEnabledFor(logging.INFO):
                log.info('calling class-based view function %s.%s.%s' % (request.dmp_router_module, request.dmp_router_class, request.dmp_router_function))
            response = func_obj(request)

            # send the post-signal
            if DMP_OPTIONS.get('SIGNALS', False):
                for receiver, ret_response in dmp_signal_post_process_request.send(sender=sys.modules[__name__], request=request, response=response):
                    if ret_response != None:
                        response = ret_response # sets it to the last non-None in the signal receiver chain

            # if we didn't get a correct response back, send a 404
            if not isinstance(response, (HttpResponse, StreamingHttpResponse)):
                if request.dmp_router_class == None:
                    log.error('view function %s.%s failed to return an HttpResponse (or the post-signal overwrote it).  Returning Http404.' % (request.dmp_router_module, request.dmp_router_function))
                else:
                    log.error('class-based view function %s.%s.%s failed to return an HttpResponse (or the post-signal overwrote it).  Returning Http404.' % (request.dmp_router_module, request.dmp_router_class, request.dmp_router_function))
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
            log.info('received an InternalViewRedirect to %s -> %s' % (full_module_filename, request.dmp_router_function))

        except RedirectException as e: # redirect to another page
            if request.dmp_router_class == None:
                log.info('view function %s.%s redirected processing to %s' % (request.dmp_router_module, request.dmp_router_function, e.redirect_to))
            else:
                log.info('class-based view function %s.%s.%s redirected processing to %s' % (request.dmp_router_module, request.dmp_router_class, request.dmp_router_function, e.redirect_to))
            # send the signal
            if DMP_OPTIONS.get('SIGNALS', False):
                dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
            # send the browser the redirect command
            return e.get_response(request)

    # the code should never get here
    raise Exception("Django-Mako-Plus router error: The route_request() function should not have been able to get to this point.  Please notify the owner of the DMP project.  Thanks.")
