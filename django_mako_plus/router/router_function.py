from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, StreamingHttpResponse

from ..signals import dmp_signal_post_process_request, dmp_signal_pre_process_request
from ..util import DMP_OPTIONS, import_qualified

from .base import Router

import sys




########################################################################################
###   Router classes for single endpoints.  When a view is first accessed, one
###   of these "mini" routers is created for it and cached for future calls.


class ViewFunctionRouter(Router):
    '''
    Router for a view function.:
    '''
    def __init__(self, mod, func):
        self.module = mod
        self.function = func
        # create a parameter converter object specific to this function
        self.converter = None
        if DMP_OPTIONS['PARAMETER_CONVERTER'] is not None:
            try:
                self.converter = import_qualified(DMP_OPTIONS['PARAMETER_CONVERTER'])(self.function)
            except ImportError as e:
                raise ImproperlyConfigured('Cannot find PARAMETER_CONVERTER: {}'.format(str(e)))


    def get_response(self, request, *args, **kwargs):
        '''Converts urlparams, calls the view function, returns the response'''
        # convert the parameters
        if self.converter is not None:
            args, kwargs = self.converter.convert_parameters(request, *args, **kwargs)

        # send the pre-signal
        if DMP_OPTIONS['SIGNALS']:
            for receiver, ret_response in dmp_signal_pre_process_request.send(sender=sys.modules[__name__], request=request, view_args=args, view_kwargs=kwargs):
                if isinstance(ret_response, (HttpResponse, StreamingHttpResponse)):
                    return ret_response

        # call the view (which is really the view_function decorator, which converts and then calls the view)
        response = self.function(request, *args, **kwargs)

        # send the post-signal
        if DMP_OPTIONS['SIGNALS']:
            for receiver, ret_response in dmp_signal_post_process_request.send(sender=sys.modules[__name__], request=request, response=response, view_args=args, view_kwargs=kwargs):
                if ret_response is not None:
                    response = ret_response # sets it to the last non-None in the signal receiver chain

        # return the response
        return response


    def message(self, request, descriptive=True):
        if descriptive:
            return 'view function {}.{}'.format(request.dmp.module, request.dmp.function)
        return '{}.{}'.format(request.dmp.module, request.dmp.function)
