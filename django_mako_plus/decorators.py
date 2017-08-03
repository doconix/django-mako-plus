
from .util import log, DMP_OPTIONS

import inspect
from collections import defaultdict


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



###################################################################
###  A pass-through decorator that annotates with the
###  decorator args and kwargs.

ANNOTATION_DECORATOR_KEY = '_dmp_annotation_decorator'


class KeywordArgDecorator(PassthroughDecorator):
    '''
    Caches the kwargs given in annotate on the annotated function.
    Multiple decorators of the same type can be placed on the same function.

    Unless force=True, raises NotDecoratedError if cls is not decorating the function.
    '''
    DEFAULT_KWARGS = {}

    @classmethod
    def _get_list_for_class(cls, func, force=False):
        func = inspect.unwrap(func, stop=lambda f: hasattr(f, ANNOTATION_DECORATOR_KEY))  # try to get the actual function
        if not hasattr(func, ANNOTATION_DECORATOR_KEY):
            if not force:
                raise NotDecoratedError('The function is not decorated with decorator: {}'.format(cls.__qualname__))
            setattr(func, ANNOTATION_DECORATOR_KEY, defaultdict(list))
        return getattr(func, ANNOTATION_DECORATOR_KEY)[cls]

    @classmethod
    def decorate(cls, func, *args, **kwargs):
        '''Does the work of the decorator: caches the kwargs for later retrieval.'''
        updated_kwargs = cls.DEFAULT_KWARGS.copy()
        updated_kwargs.update(kwargs)
        # add the ANNOTATION_DECORATOR_KEY to the function
        cls._get_list_for_class(func, force=True).append(updated_kwargs)

    @classmethod
    def get_kwargs(cls, func):
        '''
        Returns a list of cached kwargs for this decorator type on the given function.
        It is a list because the decorator could be set more than once on a given function.
        Raises NotDecoratedError if the decorator is not on the function.
        The list will always have at least one element (or NotDecoratedError would have raised).
        '''
        return cls._get_list_for_class(func)

    @classmethod
    def is_decorated(cls, func):
        '''Returns whether the function is decorated with this decorator type'''
        try:
            cls._get_list_for_class(func)
        except NotDecoratedError:
            return False
        return True


class NotDecoratedError(Exception):
    pass



##############################################################
###   Decorators for view functions

class view_function(KeywordArgDecorator):
    '''
    A decorator to signify which view functions are "callable" by web browsers.

    Any endpoint function, such as process_request, must be decorated to be callable:

        @view_function
        function process_request(request):
            ...

    Class-based views don't need to be decorated because we allow anything that extends Django's View class.
    '''
    DEFAULT_KWARGS = {
        'converter': None,
    }

