from django.http import Http404
from django.db.models import Model, ObjectDoesNotExist

from .exceptions import RedirectException
from .util import DMP_OPTIONS, log

import inspect
from collections import namedtuple

CONVERTER_KEY = 'DEFAULT_CONVERTER'

##################################################################
###   ConversionTask object

class ConversionTask(object):
    '''
    A (mostly) data class that holds meta-information about a conversion
    task.  This object is sent into each converter function.
    '''
    def __init__(self, request, decorator_kwargs, module, function):
        self.request = request
        self.decorator_kwargs = decorator_kwargs  # the kwargs from @view_function(...) decorator on the view function
        self.module = module
        self.function = function

        # set up the converter
        decorator_converter = self.decorator_kwargs.get('converter')
        if decorator_converter is None:
            self.converter = DefaultConverter()
        elif callable(decorator_converter):  # if a function (or any other callable), it is ready as is
            self.converter = decorator_converter
        else:
            raise ValueError('Invalid converter specified @view_function decorator for view.')



##################################################################
###   Default converter class

ConverterInfo = namedtuple('ConverterInfo', ( 'class_type', 'method' ))

class BaseParamConverter(object):

    @staticmethod
    def convert_method(*class_types):
        '''
        Decorator for converter methods in DefaultConverter.
        '''
        def inner(func):
            func._convert_method_types = class_types
            return func
        return inner

    def __init__(self):
        # Discover the converters in this object - these were placed here by the @convert_method decorator.
        self.converters = []
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, '_convert_method_types'):
                for class_type in method._convert_method_types:
                    pos = 0
                    for cinfo in self.converters:
                        if issubclass(class_type, cinfo.class_type):
                            break
                        pos += 1
                    if pos < len(self.converters) and class_type == self.converters[pos].class_type:
                        self.converters[pos] = ConverterInfo(class_type, method)
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
                        decorator_kwargs:   Any kwargs from the @view_function(n1=v1, n2=v2, ...) decorator.
                                            This allows you to pass view-function-specific settings to common converters.

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



class DefaultConverter(BaseParamConverter):
    '''
    The default converter that comes with DMP.  URL parameter converters
    can be any callable.  This implementation is an extensible class with pluggable
    methods for conversion of different types.

    Converters are any type of callable; see __call__ below for the primary method.
    '''
    @BaseParamConverter.convert_method(str)
    def convert_str(self, value, parameter, task):
        '''Pass through for strings'''
        return value

    @BaseParamConverter.convert_method(int, float, bool)
    def convert_builtin(self, value, parameter, task):
        '''Converts the string to float'''
        try:
            return parameter.type(value)
        except Exception as e:
            log.warning('Raising Http404 due to parameter conversion error: {}'.format(e))
            raise Http404('Invalid parameter specified in the url')

    @BaseParamConverter.convert_method(Model)  # django models.Model
    def convert_id_to_model(self, value, parameter, task):
        '''
        Converts a urlparam id to a model object.
            - The primary key (id) is expected to be an int (standard django way of doing it).
            - An empty string or dash "-" returns None.  This parameter 2 in /urlparam1/-/urlparam3 to
              signify no model (None).
            - Anything else raises Http404, including a DoesNotExist on the .get() call.
        '''
        if not value or value.strip() == '-':
            return None
        try:
            pk = int(value)
        except Exception as e:
            log.warning('Raising Http404 due to parameter conversion error: {}'.format(e))
            raise Http404('Invalid parameter specified in the url')
        try:
            return parameter.type.objects.get(pk=pk)
        except ObjectDoesNotExist as e:
            log.warning('Raising Http404 due to parameter conversion error: {}'.format(e))
            raise Http404('Invalid parameter specified in the url')


