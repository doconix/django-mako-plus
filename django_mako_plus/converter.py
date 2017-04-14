from django.http import Http404
from django.db.models import Model, ObjectDoesNotExist

from .exceptions import RedirectException
from .util import DMP_OPTIONS, log

import inspect
from collections import namedtuple


##################################################################
###   ConversionTask object

class ConversionTask(object):
    '''
    A (mostly) data class that holds meta-information about a conversion
    task.  This object is sent into each converter function.
    '''
    def __init__(self, request, module, function, kwargs):
        self.converter = _check_converter(kwargs.get('converter'))
        self.request = request
        self.module = module
        self.function = function
        self.kwargs = kwargs       # kwargs from the @view_function decorator



##################################################################
###   Default converter class

CONVERT_TYPES_KEY = '_convert_method_types'
ConverterInfo = namedtuple('ConverterInfo', ( 'class_type', 'method' ))

class BaseConverter(object):

    @staticmethod
    def convert_method(*class_types):
        '''
        Decorator for converter methods in DefaultConverter.
        '''
        def inner(func):
            setattr(func, CONVERT_TYPES_KEY, class_types)
            return func
        return inner


    def __init__(self):
        # Discover the converters in this object - these were placed here by the @convert_method decorator.
        self.converters = []
        for name, method in inspect.getmembers(self, inspect.ismethod):
            class_types = getattr(method, CONVERT_TYPES_KEY, ())
            for class_type in class_types:
                # add so the order is from most specific to most general type
                pos = 0
                for cinfo in self.converters:
                    if issubclass(class_type, cinfo.class_type):
                        break
                    pos += 1
                # if two methods convert the same type, keep the second one
                if pos < len(self.converters) and class_type == self.converters[pos].class_type:
                    self.converters[pos] = ConverterInfo(class_type, method)
                # otherwise, insert here so specialized types will match before inherited types
                else:
                    self.converters.insert(pos, ConverterInfo(class_type, method))


    def __call__(self, value, parameter, task):
        '''
        Converts the given value to the type expected by the view function.

            value:      value from request.urlparams to convert
                        The value will always be a string, even if empty '' (never None).

            parameter:  an instance of ViewParameter.  See that class above for more information.

            task:       meta-information about the current conversion task (as a named tuple):
                        module:             A reference to the module containing the view function.
                        function:           A reference to the view function.
                        converter:          A reference to the currently-running converter callable.
                        urlparams:          The unconverted request.urlparams list of strings from the url,
                                            provided for cases when converting a value depends on another.

        This method should return one of the following:

            1. Converted value (desired type is in parameter.type) to be placed in converted_args.

            2. An HttpResponse object, which is immediately returned to the browser (without further processing).

            3. Raise an exception to signal an error or validation problem, such as:
                a. Django's Http404 exception (returns immediately to the browser)
                b. DMP's RedirectException (sends a redirect to the browser)
                c. DMP's InternalRedirectException (internally restarts the router with a new view function)
               See the @view_parameter decorator for more information on handling conversion errors.
        '''
        # we don't convert anything without type hints
        if parameter.type is inspect.Parameter.empty:
            return value

        # if the value is already the right type, return it
        if isinstance(value, parameter.type):
            return value

        # find the converter method for this type
        # I'm iterating through the list to find the most specific match first
        # The list is sorted by specificity so subclasses come first
        for match_cls, func in self.converters:
            if issubclass(parameter.type, match_cls):
                return func.__get__(self, self.__class__)(value, parameter, task)

        # if we get here, we don't have a converter for this type
        if parameter.type is inspect.Parameter.empty:
            raise ValueError('Cannot convert parameter named {} because it has no type hint and CONVERT_WITHOUT_TYPE_HINTS is True'.format(parameter.name))
        raise ValueError('No parameter converter exists for type: {}'.format(parameter.type))



class DefaultConverter(BaseConverter):
    '''
    The default converter that comes with DMP.  URL parameter converters
    can be any callable.  This implementation is an extensible class with pluggable
    methods for conversion of different types.

    Converters are any type of callable; see __call__ below for the primary method.
    '''
    # characters that mean None values in URLs
    EMPTY_CHARACTERS = { '', '-', '0' }

    @BaseConverter.convert_method(str)
    def convert_str(self, value, parameter, task):
        '''Pass through for strings'''
        return value

    @BaseConverter.convert_method(int, float)
    def convert_int_float(self, value, parameter, task):
        '''Converts the string to float'''
        try:
            return parameter.type(value)
        except Exception as e:
            log.warning('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')

    @BaseConverter.convert_method(bool)
    def convert_boolean(self, value, parameter, task):
        '''Converts the string to float'''
        try:
            return value not in self.EMPTY_CHARACTERS
        except Exception as e:
            log.warning('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')

    @BaseConverter.convert_method(Model)  # django models.Model
    def convert_id_to_model(self, value, parameter, task):
        '''
        Converts a urlparam id to a model object.
            - The primary key (id) is expected to be an int (standard django way of doing it).
            - An empty string, dash "-", or 0 returns None.
            - Anything else raises Http404, including a DoesNotExist on the .get() call.
        '''
        if value in self.EMPTY_CHARACTERS:
            return None
        try:
            pk = int(value)
        except Exception as e:
            log.warning('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')
        try:
            return parameter.type.objects.get(id=pk)
        except ObjectDoesNotExist as e:
            log.warning('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')



####################################################
###   Setting and getting of default converter

DEFAULT_CONVERTER_KEY = '_dmp_default_converter'

def _check_converter(converter):
    if converter is None:
        return get_default_converter()
    elif inspect.isclass(converter):
        if hasattr(converter, '__call__'):
            return converter()
        else:
            raise ValueError('Converters must be callable or classes that implements the __call__ method.')
    elif callable(converter):
        return converter
    raise ValueError('Converters must be callable or classes that implements the __call__ method.')


def set_default_converter(converter=DefaultConverter):
    '''
    Sets the default converter used for view function parameters.

    `converter` should be a callable or a class with a __call__ method.
    If None, the system returns to the default DMP converter.
    '''
    DMP_OPTIONS[DEFAULT_CONVERTER_KEY] = _check_converter(converter)


def get_default_converter():
    '''
    Returns the default converter in the DMP system.
    '''
    return DMP_OPTIONS[DEFAULT_CONVERTER_KEY]


# set the intiial converter for the system
set_default_converter()