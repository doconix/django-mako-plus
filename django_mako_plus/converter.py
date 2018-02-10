from django.apps import apps
from django.db.models import Model, ObjectDoesNotExist
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest

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

            value:      value from request.dmp.urlparams to convert
                        The value will always be a string, even if empty '' (never None).

            parameter:  an instance of ViewParameter.  See that class above for more information.

            task:       meta-information about the current conversion task (as a named tuple):
                        module:             A reference to the module containing the view function.
                        function:           A reference to the view function.
                        converter:          A reference to the currently-running converter callable.
                        urlparams:          The unconverted request.dmp.urlparams list of strings from the url,
                                            provided for cases when converting a value depends on another.

        This method should do one of the following:

            1. Return the converted value (desired type is in parameter.type) to be placed in converted_args.

            2. Raise an exception to signal an error or validation problem, such as:
                    a. ValueError if unconvertable value (caught by DMP and and raises Http404)
                    b. DMP's RedirectException
                    c. DMP's InternalRedirectException
                    d. Django's Http404 exception
                    e. Any other exception (caught by DMP and and raises Http404)
               See the @view_parameter decorator for more information on handling conversion errors.
        '''
        # we don't convert anything without type hints
        if parameter.type is inspect.Parameter.empty:
            return value

        # find the converter method for this type
        # I'm iterating through the list to find the most specific match first
        # The list is sorted by specificity so subclasses come first
        for ci in self.converters:
            if issubclass(parameter.type, ci.convert_type):
                return ci.convert_func.__get__(self, self.__class__)(value, parameter, task)

        # we should never get here because DefaultConverter below has a converter for <object>
        # (unless a project entirely swaps out the DefaultConverter for another subclass)
        raise ValueError('No parameter converter exists for type: {}. Either remove the type hint or subclass the DMP DefaultConverter class.'.format(parameter.type))



class DefaultConverter(BaseConverter):
    '''
    The default converter that comes with DMP.  URL parameter converters
    can be any callable.  This implementation is an extensible class with pluggable
    methods for conversion of different types.

    The processing function is in super: BaseConverter.__call__().
    '''
    def _check_default(self, value, parameter, task, default_chars):
        '''Returns the default if the value is "empty"'''
        # not using a set here because it fails when value is unhashable
        if value in default_chars:
            if parameter.default is inspect.Parameter.empty:
                raise ValueError('Value was empty, but no default value is given in view function for parameter: {} ({})'.format(parameter.position, parameter.name))
            return parameter.default
        return value


    @BaseConverter.convert_method(HttpRequest)
    def convert_http_request(self, value, parameter, task):
        '''
        Pass through for the request object (first parameter in every view call).
        The request is run through the conversion process for consistency in parameter handling,
        but I can't see a reason it would ever need to be "converted" outside of middleware.
        '''
        return value


    @BaseConverter.convert_method(object)
    def convert_object(self, value, parameter, task):
        '''
        Fallback converter when nothing else matches:
            '', None convert to parameter default
            Anything else is returned as-is
        '''
        return self._check_default(value, parameter, task, ( '', None ))


    @BaseConverter.convert_method(str)
    def convert_str(self, value, parameter, task):
        '''
        Converts to string:
            '', None convert to parameter default
            Anything else is returned as-is (url params are already strings)
        '''
        return self._check_default(value, parameter, task, ( '', None ))


    @BaseConverter.convert_method(int, float)
    def convert_number(self, value, parameter, task):
        '''
        Converts to int or float:
            '', '-', None convert to parameter default
            Anything else uses int() or float() constructor
        '''
        value = self._check_default(value, parameter, task, ( '', '-', None ))
        if value is None or isinstance(value, (int, float)):
            return value
        return parameter.type(value)  # int() or float()


    @BaseConverter.convert_method(decimal.Decimal)
    def convert_decimal(self, value, parameter, task):
        '''
        Converts to decimal.Decimal:
            '', '-', None convert to parameter default
            Anything else uses Decimal constructor
        '''
        value = self._check_default(value, parameter, task, ( '', '-', None ))
        if value is None or isinstance(value, decimal.Decimal):
            return value
        return decimal.Decimal(value)


    @BaseConverter.convert_method(bool)
    def convert_boolean(self, value, parameter, task, default=False):
        '''
        Converts to boolean (only the first char of the value is used):
            '', '-', None convert to parameter default
            'f', 'F', '0', False always convert to False
            Anything else converts to True.
        '''
        value = self._check_default(value, parameter, task, ( '', '-', None ))
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and len(value) > 0:
            value = value[0]
        return value not in ( 'f', 'F', '0', False, None )


    @BaseConverter.convert_method(datetime.datetime)
    def convert_datetime(self, value, parameter, task):
        '''
        Converts to datetime.datetime:
            '', '-', None convert to parameter default
            The first matching format in settings.DATETIME_INPUT_FORMATS converts to datetime
        '''
        value = self._check_default(value, parameter, task, ( '', '-', None ))
        if value is None or isinstance(value, datetime.datetime):
            return value
        for fmt in settings.DATETIME_INPUT_FORMATS:
            try:
                return datetime.datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                continue
        raise ValueError("'{}' does not match a format in settings.DATETIME_INPUT_FORMATS".format(value))


    @BaseConverter.convert_method(datetime.date)
    def convert_date(self, value, parameter, task):
        '''
        Converts to datetime.date:
            '', '-', None convert to parameter default
            The first matching format in settings.DATE_INPUT_FORMATS converts to datetime
        '''
        value = self._check_default(value, parameter, task, ( '', '-', None ))
        if value is None or isinstance(value, datetime.date):
            return value
        for fmt in settings.DATE_INPUT_FORMATS:
            try:
                return datetime.datetime.strptime(value, fmt).date()
            except (ValueError, TypeError):
                continue
        raise ValueError("'{}' does not match a format in settings.DATE_INPUT_FORMATS".format(value))


    @BaseConverter.convert_method(Model)  # django models.Model
    def convert_id_to_model(self, value, parameter, task):
        '''
        Converts to a Model object.
            '', '-', '0', None convert to parameter default
            Anything else is assumed an object id and sent to `.get(id=value)`.
        '''
        value = self._check_default(value, parameter, task, ( '', '-', '0', None ))
        if isinstance(value, (int, str)):  # only convert if we have the id
            return parameter.type.objects.get(id=value)
        return value


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