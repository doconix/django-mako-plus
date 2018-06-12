from django.apps import apps
from django.core.exceptions import ImproperlyConfigured, ViewDoesNotExist
from django.http import HttpResponse, StreamingHttpResponse, Http404, HttpResponseServerError

from ..decorators import BaseDecorator
from ..signals import dmp_signal_post_process_request, dmp_signal_pre_process_request, dmp_signal_internal_redirect_exception, dmp_signal_redirect_exception
from ..util import import_qualified, log
from ..exceptions import InternalRedirectException, RedirectException

import inspect
import sys
import functools

# key we use to attach the converter to the view function (also see discover.py)
CONVERTER_ATTRIBUTE_NAME = 'parameter_converter'


##########################################
###   View-function decorator

class view_function(BaseDecorator):
    '''
    A decorator to signify which view functions are "callable" by web browsers.
    and to convert parameters using type hints, if provided.

    All endpoint functions, such as process_request, must be decorated as:

        @view_function
        function process_request(request):
            ...

    Or:

        @view_function(...)
        function process_request(request):
            ...
    '''
    # singleton set of decorated functions
    DECORATED_FUNCTIONS = set()


    def __init__(self, decorator_function, *args, **kwargs):
        '''Create a new wrapper around the decorated function'''
        super().__init__(decorator_function, *args, **kwargs)
        real_func = inspect.unwrap(decorator_function)

        # flag the function as an endpoint. doing it on the actual function because
        # we don't know the order of decorators on the function. order only matters if
        # the other decorators don't use @wraps correctly .in that case, @view_function
        # will put DECORATED_KEY on the decorator function rather than the real function.
        # but even that is fine *as long as @view_function is listed first*.
        self.DECORATED_FUNCTIONS.add(real_func)


    @classmethod
    def is_decorated(cls, f):
        '''Returns True if the given function is decorated with @view_function'''
        real_func = inspect.unwrap(f)
        return real_func in cls.DECORATED_FUNCTIONS



#############################################
###  Per-request wrapper for view functions

class RequestViewWrapper(object):
    '''
    A wrapper for the view function, created for each request. This is different than
    @view_function above because @view_function wraps the function one time -- like
    a normal decorator.  This decorator is used like a normal function (no @ syntax)
    and is placed *each* time a request comes through.  It must be created per request
    because we need to store the RoutingInfo object in it (which is different each request).

    Back story: Django creates its own ResolverMatch object during url resolution -- replacing
    the one we create in resolver.py. This makes it difficult to send the RoutingData object,
    through to the rest of the request.  Since the only thing Django keeps from our ResolverMatch
    is the function + args + kwargs, we need to stash the object in one of those.

    This per-request decorator also does parameter conversion, triggers signals,
    and loop RedirectExceptions.
    '''
    # FYI, not using BaseDecorator super because its metaclass
    # expects the function in the constructor arguments.

    def __init__(self, routing_data):
        self.routing_data = routing_data
        # take name and attributes of the view function
        functools.update_wrapper(self, self.routing_data.callable)


    def __call__(self, request, *args, **kwargs):
        log.info('%s', self.routing_data)
        dmp = apps.get_app_config('django_mako_plus')

        # the middleware attaches the routing data to request.dmp, but the
        # middleware is optional. let's attach it here again for those not
        # using the middleware
        request.dmp = self.routing_data

        # an outer try that catches the redirect exceptions
        try:

            # convert the parameters (the converter is placed on the func in discover.py)
            converter = getattr(self.routing_data.callable, CONVERTER_ATTRIBUTE_NAME, None)
            if converter is not None:
                args, kwargs = converter.convert_parameters(request, *args, **kwargs)

            # send the pre-signal
            if dmp.options['SIGNALS']:
                for receiver, ret_response in dmp_signal_pre_process_request.send(sender=sys.modules[__name__], request=request, view_args=args, view_kwargs=kwargs):
                    if isinstance(ret_response, (HttpResponse, StreamingHttpResponse)):
                        return ret_response

            # call the view function
            response = self.routing_data.callable(request, *args, **kwargs)
            if not isinstance(response, (HttpResponse, StreamingHttpResponse)):
                log.info('%s failed to return an HttpResponse (or the post-signal overwrote it).  Returning 500 error.', self.routing_data.callable)
                return HttpResponseServerError('Invalid response received from server.')

            # send the post-signal
            if dmp.options['SIGNALS']:
                for receiver, ret_response in dmp_signal_post_process_request.send(sender=sys.modules[__name__], request=request, response=response, view_args=args, view_kwargs=kwargs):
                    if ret_response is not None:
                        response = ret_response # sets it to the last non-None in the signal receiver chain

            return response

        except InternalRedirectException as ivr:
            # send the signal
            if dmp.options['SIGNALS']:
                dmp_signal_internal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=ivr)
            # update the RoutingData object
            request.dmp.module = ivr.redirect_module
            request.dmp.function = ivr.redirect_function
            try:
                request.dmp.callable = getattr(import_qualified(request.dmp.module), request.dmp.function)
            except (ImportError, AttributeError):
                log.info('could not fulfill InternalViewRedirect because %s.%s does not exist.', request.dmp.module, request.dmp.function)
                raise Http404()
            # recurse with this routing data
            log.info('received an InternalViewRedirect to %s.%s', request.dmp.module, request.dmp.function)
            return RequestViewWrapper(self.routing_data)(request, *args, **kwargs)

        except RedirectException as e: # redirect to another page
            log.info('view %s.%s redirected processing to %s', request.dmp.module, request.dmp.function, e.redirect_to)
            # send the signal
            if dmp.options['SIGNALS']:
                dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
            # send the browser the redirect command
            return e.get_response(request)

        # the code should never get here
