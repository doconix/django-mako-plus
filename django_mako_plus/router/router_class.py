from django.http import HttpResponseNotAllowed

from ..util import log
from .base import Router
from .decorators import view_function
from .router_function import ViewFunctionRouter



class ClassBasedRouter(Router):
    '''
    Router for class-based views.

    A class-based router can have several endpoints, such as get(),
    post(), or put().  A ViewFunctionRouter is created for each
    of the endpoints that exist in the given class.  So this is really
    just a meta-router that reroutes to the appropriate ViewFunctionRouter
    within it.
    '''
    def __init__(self, module, instance):
        self.instance = instance
        self.endpoints = {}
        for mthd_name in instance.http_method_names:  # get parameters from the first http-based method (get, post, etc.)
            func = getattr(instance, mthd_name, None)
            if func is not None:
                # class-based methods don't explicitly have to be decorated with @view_function.
                # they don't need that security because, by subclassing View, we know they are endpoints.
                # but we still need the view_function decorator for the parameter conversion, so we wrap
                # if needed.
                if not view_function._is_decorated(func):
                    func = view_function(func)
                self.endpoints[mthd_name] = ViewFunctionRouter(module, func)


    def get_response(self, request, *args, **kwargs):
        endpoint = self.endpoints.get(request.method.lower())
        if endpoint is not None:
            return endpoint.get_response(request, **kwargs)
        log.info('Method Not Allowed (%s): %s', request.method, request.path, extra={'status_code': 405, 'request': request})
        return HttpResponseNotAllowed([ e.upper() for e in self.endpoints.keys() ])


    @property
    def name(self):
        return self.instance.__class__.__qualname__


    def message(self, request, descriptive=True):
        if descriptive:
            return 'class-based view function {}.{}.{}'.format(request.dmp.module, self.name, request.dmp.function)
        return '{}.{}.{}'.format(request.dmp.module, self.name, request.dmp.function)
