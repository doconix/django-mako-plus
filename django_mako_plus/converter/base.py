from django.apps import apps

from ..util import log, qualified_name
from .info import ConverterInfo
from .exceptions import ConvertException

import inspect
from operator import attrgetter
import logging


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

            parameter:  an instance of ViewParameter.  See the class in router.py for more information.

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

                try:
                    return ci.convert_func.__get__(self, self.__class__)(value, parameter, task)

                except Exception as exc:
                    raise ConvertException(
                        message=str(exc),
                        value=value,
                        parameter=parameter,
                        task=task,
                        exc=exc,
                    )

        # we should never get here because DefaultConverter below has a converter for <object>
        # (unless a project entirely swaps out the DefaultConverter for another subclass)
        raise ConvertException(
            message='No parameter converter exists for type: {}. Either remove the type hint or subclass the DMP DefaultConverter class.'.format(parameter.type),
            value=value,
            parameter=parameter,
            task=task,
        )
