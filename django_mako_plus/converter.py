from django.apps import apps
from django.db.models import Model, ObjectDoesNotExist
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404

from .exceptions import RedirectException
from .util import DMP_OPTIONS, log

import inspect, datetime, decimal, sys
from collections import namedtuple
from operator import attrgetter


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
###   ConverterInfo class: see @convert_method below

class ConverterInfo(object):
    '''
    Used by @convert_method to track types on a converter method.
    '''
    CONVERT_TYPES_KEY = '_dmp_converter_infos'
    DECLARED_ORDER = 0

    def __init__(self, convert_type, convert_func):
        self.convert_type = convert_type
        self.convert_func = convert_func
        self.sort_key = None
        self.declared_order = ConverterInfo.DECLARED_ORDER  # order it was declared in source code
        ConverterInfo.DECLARED_ORDER = 0 if ConverterInfo.DECLARED_ORDER == sys.maxsize else ConverterInfo.DECLARED_ORDER + 1
        
    def _delayed_init(self):
        # we allow the type for models to be declared as a string, such as "auth.User"
        # because real types can't be referenced until Django finishes initialization
        # switch any strings over to the real type now
        if isinstance(self.convert_type, str):
            try:
                app_name, model_name = self.convert_type.split('.')
            except ValueError:
                raise ImproperlyConfigured('"{}" is not a valid converter type. String-based converter types must be specified in "app.Model" format.'.format(self.convert_type))
            try:
                self.convert_type = apps.get_model(app_name, model_name)
            except LookupError as e:
                raise ImproperlyConfigured('"{}" is not a valid model name. {}'.format(self.convert_type, e))
        
        # we reverse sort by ( len(mro), source code order ) so subclasses match first
        # on same types, last declared method sorts first
        self.sort_key = ( -1 * len(inspect.getmro(self.convert_type)), -1 * self.declared_order )


##################################################################
###   Default converter class


class BaseConverter(object):

    @staticmethod
    def convert_method(*class_types):
        '''
        Decorator for converter methods in DefaultConverter.
        '''
        def inner(func):
            setattr(func, ConverterInfo.CONVERT_TYPES_KEY, [ ConverterInfo(ct, func) for ct in class_types ])
            return func
        return inner


    def __init__(self):
        self.converters = []
        self._delayed_init_run = False
        
    
    def _delayed_init(self):
        '''
        Populates the registry of types to converters for this Converter object.  This method is
        called each time a request is processed, so if overridden, be sure to short circuit as needed.
        This implementation short circuits until all apps are ready.
        '''
        # This is called by _check_converter() below, and it is delayed (instead of using __init__)
        # because model class strings can't be switched to models until the app registry is populated.  
        # This could be called once from DMP's AppConfig.ready(), but since each view function can have
        # a separate converters, and since the default converter can be changed at any time, I'm doing
        # it when a ConversionTask object is created (part of DMP request processing).
        if self._delayed_init_run or not apps.ready:
            return
        self._delayed_init_run = True
        
        # converter methods within this class (subclass) were tagged earlier by the decorator
        # with the CONVERT_TYPES_KEY.  go through all methods in this class (subclass) and 
        # gather the ConverterInfo objects into a big list
        for name, method in inspect.getmembers(self, inspect.ismethod):
            self.converters.extend(getattr(method, ConverterInfo.CONVERT_TYPES_KEY, ()))
            
        # allow each ConverterInfo to init, such as convert any model string "auth.User" to real class type
        for ci in self.converters:
            ci._delayed_init()
            
        # sort the most specialized types to be first.  this allows subclass types to match instead 
        # of their superclasses (if both are in the list).
        self.converters.sort(key=attrgetter('sort_key'))


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
        for ci in self.converters:
            if issubclass(parameter.type, ci.convert_type):
                return ci.convert_func.__get__(self, self.__class__)(value, parameter, task)

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
    EMPTY_CHARACTERS = { '', '-', '0', None }

    @BaseConverter.convert_method(str)
    def convert_str(self, value, parameter, task):
        '''Pass through for strings'''
        return value


    @BaseConverter.convert_method(int, float)
    def convert_number(self, value, parameter, task):
        '''Converts the string to an int or float'''
        if value is None:
            value = 0
        try:
            return parameter.type(value)  # int() or float()
        except Exception as e:
            log.info('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')


    @BaseConverter.convert_method(decimal.Decimal)
    def convert_decimal(self, value, parameter, task):
        '''Converts the string to a decimal.Decimal'''
        try:
            if value in self.EMPTY_CHARACTERS:
                return None
        except TypeError:
            pass # not hashable
        try:
            return parameter.type(value)
        except Exception as e:
            log.info('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')


    @BaseConverter.convert_method(bool)
    def convert_boolean(self, value, parameter, task):
        '''Converts the string to float'''
        try:
            return value is not False and value not in self.EMPTY_CHARACTERS
        except Exception as e:
            log.info('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')


    @BaseConverter.convert_method(datetime.datetime)
    def convert_datetime(self, value, parameter, task):
        '''Converts the string to datetime.datetime'''
        try:
            if value in self.EMPTY_CHARACTERS:
                return None
        except TypeError:
            pass # not hashable
        try:
            for fmt in settings.DATETIME_INPUT_FORMATS:
                try:
                    return datetime.datetime.strptime(value, fmt)
                except (ValueError, TypeError):
                    continue
            raise ValueError("value '{}' does not match any formats in settings.DATETIME_INPUT_FORMATS".format(value))
        except Exception as e:
            log.info('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')


    @BaseConverter.convert_method(datetime.date)
    def convert_date(self, value, parameter, task):
        '''Converts the string to datetime.date'''
        try:
            if value in self.EMPTY_CHARACTERS:
                return None
        except TypeError:
            pass # not hashable
        try:
            for fmt in settings.DATE_INPUT_FORMATS:
                try:
                    return datetime.datetime.strptime(value, fmt).date()
                except (ValueError, TypeError):
                    continue
            raise ValueError("value '{}' does not match any formats in settings.DATE_INPUT_FORMATS".format(value))
        except Exception as e:
            log.info('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')


    @BaseConverter.convert_method(Model)  # django models.Model
    def convert_id_to_model(self, value, parameter, task):
        '''
        Converts a urlparam id to a model object.
            - The primary key (id) is expected to be an int (standard django way of doing it).
            - An empty string, dash "-", or 0 returns None.
            - Anything else raises Http404, including a DoesNotExist on the .get() call.
        '''
        try:
            if value in self.EMPTY_CHARACTERS:
                return None
        except TypeError:
            pass # not hashable
        try:
            pk = int(value)
        except Exception as e:
            log.info('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')
        try:
            return parameter.type.objects.get(id=pk)
        except ObjectDoesNotExist as e:
            log.info('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')



####################################################
###   Setting and getting of default converter

DEFAULT_CONVERTER_KEY = '_dmp_default_converter'

def _check_converter(converter):
    '''
    Checks the given converter and returns a (potentially) modified converter.
    If None: returns the system default converter.
    If a class: returns an instance of the class.
    '''
    # default or instantiate if necessary
    if converter is None:
        converter = get_default_converter()
    elif inspect.isclass(converter): 
        converter = converter()
    # ensure callable
    if not callable(converter):
        raise ValueError('Converters must be callable or classes that implements the __call__ method.')
    # if a subclass of BaseConverter, allow it to initialize
    if isinstance(converter, BaseConverter):
        converter._delayed_init()
    # return
    return converter


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