from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.http import Http404

from ..converter import ConversionTask
from ..exceptions import BaseRedirectException
from ..signals import dmp_signal_post_process_request, dmp_signal_pre_process_request
from ..util import DMP_OPTIONS, log

from .base import Router
from ..converter import ViewParameter

import inspect
import sys




########################################################################################
###   Router classes for single endpoints.  When a view is first accessed, one
###   of these "mini" routers is created for it and cached for future calls.


class ViewFunctionRouter(Router):
    '''
    Router for a view function.  This class:

    1. Converts the url parameters.
    2. Calls the endpoint (view function).  This, finally, is where DMP
       hands control over to the project's real view function.
    3. Calls pre and post process_request signals.
    '''
    def __init__(self, mod, func, decorator_kwargs):
        self.module = mod
        self.function = func
        self.decorator_kwargs = decorator_kwargs
        self.signature = inspect.signature(func)
        # map the type hints
        param_types = getattr(func, '__annotations__', {})  # not using typing.get_type_hints because it adds Optional() to None defaults, and we don't need to follow mro here
        # inspect the parameters of the view function
        params = []
        for i, p in enumerate(self.signature.parameters.values()):
            params.append(ViewParameter(
                name=p.name,
                position=i,
                kind=p.kind,
                type=param_types.get(p.name) or inspect.Parameter.empty,
                default=p.default,
            ))
        self.parameters = tuple(params)


    def get_response(self, *args, **kwargs):
        '''Converts urlparams, calls the view function, returns the response'''
        # leaving request inside *args (or kwargs) so we can convert it like anything else (and parameter indices aren't off by one)
        request = kwargs.get('request', args[0])
        ctask = ConversionTask(
            request=request,
            module=self.module,
            function=self.function,
            view_function_kwargs=self.decorator_kwargs,
        )
        args = list(args)
        urlparam_i = 0
        # add urlparams into the arguments and convert the values
        for parameter_i, parameter in enumerate(self.parameters):
            # skip *args, **kwargs
            if parameter.kind is inspect.Parameter.VAR_POSITIONAL or parameter.kind is inspect.Parameter.VAR_KEYWORD:
                pass
            # value in kwargs?
            elif parameter.name in kwargs:
                kwargs[parameter.name] = ctask.convert_value(kwargs[parameter.name], parameter)
            # value in args?
            elif parameter_i < len(args):
                args[parameter_i] = ctask.convert_value(args[parameter_i], parameter)
            # urlparam value?
            elif urlparam_i < len(request.dmp.urlparams):
                kwargs[parameter.name] = ctask.convert_value(request.dmp.urlparams[urlparam_i], parameter)
                urlparam_i += 1
            # can we assign a default value?
            elif parameter.default is not inspect.Parameter.empty:
                kwargs[parameter.name] = ctask.convert_value(parameter.default, parameter)
            # fallback is None
            else:
                kwargs[parameter.name] = ctask.convert_value(None, parameter)

        # send the pre-signal
        if DMP_OPTIONS['SIGNALS']:
            for receiver, ret_response in dmp_signal_pre_process_request.send(sender=sys.modules[__name__], request=request, view_args=args, view_kwargs=kwargs):
                if isinstance(ret_response, (HttpResponse, StreamingHttpResponse)):
                    return ret_response

        # call the view!
        response = self.function(*args, **kwargs)

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
