from .converter import DefaultConverter
from .util import log, DMP_OPTIONS

import inspect
from collections import defaultdict, namedtuple


################################################################
###  An abstract pass-through decorator.

_UNDEFINED_FUNCTION = object()

class PassthroughDecorator(object):
    '''
    A pass-through decorator that can be called with @decorator or @decorator(a=1, b=2).
    The decorate() method is called to perform the behavior of the decorator on the function.
    This class instance does not stay in the decorator call chain.  The primary use case
    of this decorator is place an attribute on the function.

    @wraps is not used with this because it is a pass-through.  The decorator disappears
    after doing its initial work and does not stay within the call chain.

    Note that it is not possible to use this decorator with the first argument being a callable
    because Python will take it as the decorated function.
    '''
    def __new__(cls, func=_UNDEFINED_FUNCTION, *args, **kwargs):
        # if we have a function, it was called without arguments: @decorator
        # annotate and return the function (an instance never gets created)
        if func is not _UNDEFINED_FUNCTION and callable(func) and len(args) == 0 and len(kwargs) == 0:
            cls.decorate(func)
            return func

        # if we don't have a function, it was specified with arguments: @decorator(a=1, b=2)
        # we need to make an object, let __init__ run, and let python call __call__.
        return super().__new__(cls)

    def __init__(self, func=None, *args, **kwargs):
        self.args = (func, ) + args
        self.kwargs = kwargs

    def __call__(self, func):
        self.decorate(func, *self.args, **self.kwargs)
        return func

    @classmethod
    def decorate(cls, func, *args, **kwargs):
        '''Subclasses should override this method to make the annotation'''
        raise NotImplementedError('The `annotate` method must be implemented by subclasses.')




##############################################################
###   Decorators for view functions

VIEW_FUNCTION_KEY = '_dmp_view_function_'
ViewFunctionData = namedtuple('ViewFunctionData', [ 'converters' ])


DEFAULT_CONVERTERS = [
    DefaultConverter(),
]



class view_function(PassthroughDecorator):
    '''
    A decorator to signify which view functions are "callable" by web browsers.

    Any endpoint function, such as process_request, must be decorated to be callable:

        @view_function
        function process_request(request):
            ...

    Or:

        @view_function(converters=[..., ...])
        function process_request(request):
            ...

    '''
    @classmethod
    def decorate(cls, func, converters=DEFAULT_CONVERTERS):
        '''Decorates the method'''
        setattr(func, VIEW_FUNCTION_KEY, ViewFunctionData(converters))
