from django.db.models import Model
from django.conf import settings
from django.http import HttpRequest

from .base import BaseConverter

import datetime
import decimal
import inspect



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
