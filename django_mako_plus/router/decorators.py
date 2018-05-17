from ..decorators import BaseDecorator

import inspect



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
