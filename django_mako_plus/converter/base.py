from django.apps import apps
from django.db.models import Model
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpResponse, StreamingHttpResponse, Http404

from ..decorators import OptionsDecorator
from ..signals import dmp_signal_post_process_request, dmp_signal_pre_process_request
from ..util import DMP_OPTIONS, log, qualified_name
from .info import ConverterInfo
from .parameter import ViewParameter

import inspect
from operator import attrgetter
import logging
import datetime
import decimal
from collections import defaultdict, namedtuple
import sys




def parameter_converter(object):
    '''
    Decorator that Denotes a function as a url parameter converter.
    '''




class view_function(OptionsDecorator):
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
    DECORATED_KEY = '_dmp_view_function_'

    def __init__(self, decorated_function, **options):
        '''Create a new wrapper around the decorated function'''
        super().__init__(decorated_function, **options)

        # flag the function as an endpoint
        setattr(self.decorated_function, self.DECORATED_KEY, self)

        # inspect the parameters on the function
        self.signature = inspect.signature(self.decorated_function)
        param_types = getattr(self.decorated_function, '__annotations__', {})  # not using typing.get_type_hints because it adds Optional() to None defaults, and we don't need to follow mro here
        params = []
        for i, p in enumerate(self.signature.parameters.values()):
            params.append(ViewParameter(
                name=p.name,
                position=i,
                kind=p.kind,
                type=param_types.get(p.name) or inspect.Parameter.empty,
                default=p.default,
            ))
        self.parameters = tuple(params)


    @classmethod
    def is_decorated(cls, f):
        '''Returns True if the given function is decorated with @view_function'''
        return hasattr(f, cls.DECORATED_KEY)


    def __call__(self, *args, **kwargs):
        '''
        Trigger the decorated function.

        Subclasses should override convert_value if needed.
        '''
        # leaving request inside *args above (or kwargs) so we can convert it like anything else (and parameter indices aren't off by one)
        request = kwargs.get('request', args[0])

        # convert each of the parameters
        args = list(args)
        urlparam_i = 0
        # add urlparams into the arguments and convert the values
        for parameter_i, parameter in enumerate(self.parameters):
            # skip *args, **kwargs
            if parameter.kind is inspect.Parameter.VAR_POSITIONAL or parameter.kind is inspect.Parameter.VAR_KEYWORD:
                pass
            # value in kwargs?
            elif parameter.name in kwargs:
                kwargs[parameter.name] = self.convert_value(kwargs[parameter.name], parameter, request)
            # value in args?
            elif parameter_i < len(args):
                args[parameter_i] = self.convert_value(args[parameter_i], parameter, request)
            # urlparam value?
            elif urlparam_i < len(request.dmp.urlparams):
                kwargs[parameter.name] = self.convert_value(request.dmp.urlparams[urlparam_i], parameter, request)
                urlparam_i += 1
            # can we assign a default value?
            elif parameter.default is not inspect.Parameter.empty:
                kwargs[parameter.name] = self.convert_value(parameter.default, parameter, request)
            # fallback is None
            else:
                kwargs[parameter.name] = self.convert_value(None, parameter, request)

        # call the decorated view function!
        return self.decorated_function(*args, **kwargs)


    def convert_value(self, value, parameter, request):
        '''
        Converts the given value using the converter list.

        If the value cannot be converted, raise an exception.
        The DMP router processes several exceptions in useful ways:
            ValueError: the converter returns an Http404 response
            RedirectException: redirects the browser (see DMP docs)
            InternalRedirectException: redirects processing internally (see DMP docs)
            Http404: returns an Http404 response

        '''
        try:
            return converter(value, parameter)

        except ValueError as e:
            log.info('ValueError raised during conversion of parameter %s (%s): %s', parameter.position, parameter.name, e)
            raise Http404('Parameter could not be converted')

        except Exception as e:
            log.info('Exception raised during conversion of parameter %s (%s): %s', parameter.position, parameter.name, e)
            raise



    # def _delayed_init(self):
    #     '''
    #     Populates the registry of types to converters for this Converter object.  This method is
    #     called each time a request is processed, so if overridden, be sure to short circuit as needed.
    #     This implementation short circuits until all apps are ready.
    #     '''
    #     # This is called by _check_converter() below, and it is delayed (instead of using __init__)
    #     # because model class strings can't be switched to models until the app registry is populated.
    #     # This could be called once from DMP's AppConfig.ready(), but since each view function can have
    #     # a separate converters, and since the default converter can be changed at any time, I'm doing
    #     # it when a ConversionTask object is created (part of DMP request processing).
    #     if self._delayed_init_run or not apps.ready:
    #         return
    #     self._delayed_init_run = True

    #     # converter methods within this class (subclass) were tagged earlier by the decorator
    #     # with the CONVERT_TYPES_KEY.  go through all methods in this class (subclass) and
    #     # gather the ConverterInfo objects into a big list
    #     for name, method in inspect.getmembers(self, inspect.ismethod):
    #         self.converters.extend(getattr(method, ConverterInfo.CONVERT_TYPES_KEY, ()))

    #     # allow each ConverterInfo to init, such as convert any model string "auth.User" to real class type
    #     for ci in self.converters:
    #         ci._delayed_init()

    #     # sort the most specialized types to be first.  this allows subclass types to match instead
    #     # of their superclasses (if both are in the list).
    #     self.converters.sort(key=attrgetter('sort_key'))


    def __call__(self, value, parameter):
        '''
        Converts the given value to the type expected by the view function.

            value:      value from request.dmp.urlparams to convert
                        The value will always be a string, even if empty '' (never None).

            parameter:  an instance of ViewParameter.  See the class in router.py for more information.

            router:     the ViewFunctionRouter router for this endpoint.  Useful fields:
                        module:     A reference to the module containing the view function
                        function:   A reference to the view function
                        signature:  The view function signature object (see inspect module)
                        parameters: List of ViewParameter objects for the view function

            request:    The current request object.

        This method should do one of three following:

            1. Return the converted value (desired type is in parameter.type).

            2. Raise a ConversionError, which signals the router to try the next
               converter in the list of converters for the current view function.

            3. Raise any other exception, which stops the conversion process and
               sends processing back to the DMP router.  Some useful exceptions to raise:
                    - DMP's RedirectException, which sends a redirect to the browser
                    - DMP's InternalRedirectException, which calls a new endpoint function immediately
                    - Django's Http404 exception, which goes back to the browser

        '''
        # we don't convert anything without type hints
        if parameter.type is inspect.Parameter.empty:
            if log.isEnabledFor(logging.DEBUG):
                log.debug('skipping conversion of parameter `%s` because it has no type hint', parameter.name)
            return value

        # find the converter method for this type
        # I'm iterating through the list to find the most specific match first
        # The list is sorted by specificity so subclasses come first
        for ci in self.converters:
            if issubclass(parameter.type, ci.convert_type):
                if log.isEnabledFor(logging.DEBUG):
                    log.debug('converting parameter `%s` using %s', parameter.name, qualified_name(ci.convert_func))
                return ci.convert_func.__get__(self, self.__class__)(value, parameter)

        # if we get here, there wasn't a converter or this type
        raise ConversionError(message='No parameter converter exists for type: {}. Either remove the type hint or subclass the DMP DefaultConverter class.'.format(parameter.type))





    ###   Functions for various converters  ###

    def _check_default(self, value, parameter, default_chars):
        '''Returns the default if the value is "empty"'''
        # not using a set here because it fails when value is unhashable
        if value in default_chars:
            if parameter.default is inspect.Parameter.empty:
                raise ValueError('Value was empty, but no default value is given in view function for parameter: {} ({})'.format(parameter.position, parameter.name))
            return parameter.default
        return value


    @BaseConverter.convert_method(HttpRequest)
    def convert_http_request(self, value, parameter):
        '''
        Pass through for the request object (first parameter in every view call).
        The request is run through the conversion process for consistency in parameter handling,
        but I can't see a reason it would ever need to be "converted" outside of middleware.
        '''
        return value


    @BaseConverter.convert_method(object)
    def convert_object(self, value, parameter):
        '''
        Fallback converter when nothing else matches:
            '', None convert to parameter default
            Anything else is returned as-is
        '''
        return self._check_default(value, parameter, ( '', None ))


    @BaseConverter.convert_method(str)
    def convert_str(self, value, parameter):
        '''
        Converts to string:
            '', None convert to parameter default
            Anything else is returned as-is (url params are already strings)
        '''
        return self._check_default(value, parameter, ( '', None ))


    @BaseConverter.convert_method(int, float)
    def convert_number(self, value, parameter):
        '''
        Converts to int or float:
            '', '-', None convert to parameter default
            Anything else uses int() or float() constructor
        '''
        value = self._check_default(value, parameter, ( '', '-', None ))
        if value is None or isinstance(value, (int, float)):
            return value
        try:
            return parameter.type(value)  # int() or float()
        except Exception as e:
            raise ValueError(str(e))


    @BaseConverter.convert_method(decimal.Decimal)
    def convert_decimal(self, value, parameter):
        '''
        Converts to decimal.Decimal:
            '', '-', None convert to parameter default
            Anything else uses Decimal constructor
        '''
        value = self._check_default(value, parameter, ( '', '-', None ))
        if value is None or isinstance(value, decimal.Decimal):
            return value
        try:
            return decimal.Decimal(value)
        except Exception as e:
            raise ValueError(str(e))



    @BaseConverter.convert_method(bool)
    def convert_boolean(self, value, parameter, default=False):
        '''
        Converts to boolean (only the first char of the value is used):
            '', '-', None convert to parameter default
            'f', 'F', '0', False always convert to False
            Anything else converts to True.
        '''
        value = self._check_default(value, parameter, ( '', '-', None ))
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and len(value) > 0:
            value = value[0]
        return value not in ( 'f', 'F', '0', False, None )


    @BaseConverter.convert_method(datetime.datetime)
    def convert_datetime(self, value, parameter):
        '''
        Converts to datetime.datetime:
            '', '-', None convert to parameter default
            The first matching format in settings.DATETIME_INPUT_FORMATS converts to datetime
        '''
        value = self._check_default(value, parameter, ( '', '-', None ))
        if value is None or isinstance(value, datetime.datetime):
            return value
        for fmt in settings.DATETIME_INPUT_FORMATS:
            try:
                return datetime.datetime.strptime(value, fmt)
            except (ValueError, TypeError):
                continue
        raise ValueError("`{}` does not match a format in settings.DATETIME_INPUT_FORMATS".format(value))


    @BaseConverter.convert_method(datetime.date)
    def convert_date(self, value, parameter):
        '''
        Converts to datetime.date:
            '', '-', None convert to parameter default
            The first matching format in settings.DATE_INPUT_FORMATS converts to datetime
        '''
        value = self._check_default(value, parameter, ( '', '-', None ))
        if value is None or isinstance(value, datetime.date):
            return value
        for fmt in settings.DATE_INPUT_FORMATS:
            try:
                return datetime.datetime.strptime(value, fmt).date()
            except (ValueError, TypeError):
                continue
        raise ValueError("`{}` does not match a format in settings.DATE_INPUT_FORMATS".format(value))


    @BaseConverter.convert_method(Model)  # django models.Model
    def convert_id_to_model(self, value, parameter):
        '''
        Converts to a Model object.
            '', '-', '0', None convert to parameter default
            Anything else is assumed an object id and sent to `.get(id=value)`.
        '''
        value = self._check_default(value, parameter, ( '', '-', '0', None ))
        if isinstance(value, (int, str)):  # only convert if we have the id
            try:
                return parameter.type.objects.get(id=value)
            except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
                raise Http404(str(e))
        return value
