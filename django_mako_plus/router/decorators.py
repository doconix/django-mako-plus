from ..decorator import BaseDecorator
from ..converter.base import ParameterConverter
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

    This class also converts parameters through the `converter` attribute,
    which is a django_mako_plus.converter.base.ParameterConverter object.
    '''
    # singleton set of decorated functions
    DECORATED_FUNCTIONS = set()
    # the converter class to use (subclasses can override this)
    converter_class = ParameterConverter

    def __init__(self, decorator_function, *args, **kwargs):
        '''Create a new wrapper around the decorated function'''
        super().__init__(decorator_function, *args, **kwargs)
        self.converter = self.converter_class(decorator_function) if self.converter_class is not None else None

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
        if self.converter is not None:
            args, kwargs = self.converter.convert_parameters(*args, **kwargs)

        # call the decorated view function!
        return self.decorator_function(*args, **kwargs)
