
from ..converter.base import ParameterConverter

import inspect
import functools


##########################################
###   Base decorator classes

class BaseDecoratorMeta(type):
    '''
    Metaclass that allows ourdecorator to be called
    with or without optional arguments.
    '''
    def __call__(self, *args, **kwargs):
        # if args has a single function, we'll assume it is the function we're decorating.
        # that means the syntax was `@decorator` or `@decorator()` -- no arguments
        # we need to return normally
        if len(args) == 1 and callable(args[0]):
            instance = super(BaseDecoratorMeta, self).__call__(*args, **kwargs)
            functools.update_wrapper(instance, args[0])
            return instance

        # if we get here, the syntax was `@decorator(a=1, b=2)` -- with arguments
        # python hasn't yet "called" the decorator.  we'll return a factory
        # for python to call with the decorated function
        def factory(func):
            instance = super(BaseDecoratorMeta, self).__call__(func, *args, **kwargs)
            functools.update_wrapper(instance, func)
            return instance
        return factory


class BaseDecorator(object, metaclass=BaseDecoratorMeta):
    '''
    A decorator that can be called with or without kwargs:

        @decorator
        @decorator()
        @decorator(option1=value1, option2=value2)

    '''
    def __init__(self, decorator_function, **decorator_kwargs):
        self.decorator_function = decorator_function
        # not using name `options` because Django's View class already
        # has an options() method (and this decorates that class).
        self.decorator_kwargs = decorator_kwargs

    def __get__(self, instance, type=None):
        # Called when used on a (unbound) class method - descriptor protocol
        return functools.partial(self, instance)

    def __call__(self, *args, **kwargs):
        '''Subclasses should override this method'''
        return self.decorator_function(*args, **kwargs)



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

    This class also converts parameters through the `converter` attribute,
    which is a django_mako_plus.converter.base.ParameterConverter object.
    '''
    # singleton set of decorated functions
    DECORATED_FUNCTIONS = set()
    # the converter class to use (subclasses can override this)
    converter_class = ParameterConverter

    def __init__(self, decorator_function, **kwargs):
        '''Create a new wrapper around the decorated function'''
        super().__init__(decorator_function, **kwargs)
        self.converter = self.converter_class(decorator_function)

        # flag the function as an endpoint. doing it on the actual function because
        # we don't know the order of decorators on the function. order only matters if
        # the other decorators don't use @wraps correctly .in that case, @view_function
        # will put DECORATED_KEY on the decorator function rather than the real function.
        # but even that is fine *as long as @view_function is listed first*.
        real_func = inspect.unwrap(decorator_function)
        self.DECORATED_FUNCTIONS.add(real_func)


    @classmethod
    def _is_decorated(cls, f):
        '''Returns True if the given function is decorated with @view_function'''
        real_func = inspect.unwrap(f)
        return real_func in cls.DECORATED_FUNCTIONS


    def __call__(self, *args, **kwargs):
        '''
        Called for every request.
        See the docs for this class on customizing this method.

        Note that args[0] is the request object.  We leave it in the args list
        so the convert_parameters method can index the list without
        things being off by one.
        '''
        # convert the urlparams
        args, kwargs = self.converter.convert_parameters(*args, **kwargs)

        # call the decorated view function!
        return self.decorator_function(*args, **kwargs)
