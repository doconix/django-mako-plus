from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseServerError, StreamingHttpResponse

from .factory import get_router
from .router_exception import RegistryExceptionRouter
from .routing_data import RoutingData

from ..exceptions import InternalRedirectException, RedirectException
from ..signals import dmp_signal_internal_redirect_exception, dmp_signal_redirect_exception
from ..util import DMP_OPTIONS, log

import sys



def route_request(request, *args, **kwargs):
    '''
    The main router for all calls coming in to the system.  Patterns in urls.py should call this function.
    '''
    # an outer try that catches the redirect exceptions
    try:
        # ensure the middleware ran
        if getattr(request, 'dmp', None) is None:
            raise ImproperlyConfigured("Variable request.dmp.function_obj does not exist (check MIDDLEWARE for `django_mako_plus.RequestInitMiddleware`).")

        # output the variables so the programmer can debug where this is routing
        log.info(str(request.dmp))

        # if we had a view not found, raise a 404
        if isinstance(request.dmp.function_obj, RegistryExceptionRouter):
            log.info(request.dmp.function_obj.message(request))
            return request.dmp.function_obj.get_response(request, *args, **kwargs)

        # call the function
        log.info('calling %s', request.dmp.function_obj.message(request))
        response = request.dmp.function_obj.get_response(request, *args, **kwargs)

        # if we didn't get a correct response back, send a 500
        if not isinstance(response, (HttpResponse, StreamingHttpResponse)):
            msg = '%s failed to return an HttpResponse (or the post-signal overwrote it).  Returning 500 error.' % request.dmp.function_obj.message(request)
            log.info(msg)
            return HttpResponseServerError(msg)

        # return the response
        return response

    except InternalRedirectException as ivr:
        # send the signal
        if DMP_OPTIONS['SIGNALS']:
            dmp_signal_internal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=ivr)
        # update the RoutingData object
        request.dmp.module = ivr.redirect_module
        request.dmp.function = ivr.redirect_function
        request.dmp._set_function_obj(request, get_router(request.dmp.module, request.dmp.function, verify_decorator=False))
        if isinstance(request.dmp.function_obj, RegistryExceptionRouter):
            log.info('could not fulfill InternalViewRedirect because %s.%s does not exist.', request.dmp.module, request.dmp.function)
        # recurse with the same info
        log.info('received an InternalViewRedirect to %s.%s', request.dmp.module, request.dmp.function)
        return route_request(request, *args, **kwargs)

    except RedirectException as e: # redirect to another page
        if request.dmp.class_obj is None:
            log.info('%s redirected processing to %s', request.dmp.function_obj.message(request), e.redirect_to)
        # send the signal
        if DMP_OPTIONS['SIGNALS']:
            dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
        # send the browser the redirect command
        return e.get_response(request)

    # the code should never get here
