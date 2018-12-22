from django.db.models import Model
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpRequest

from .decorators import parameter_converter

import inspect
import datetime
import decimal



###   object (fallback if nothing else matches)  ###

@parameter_converter(object)
def convert_object(value, parameter):
    '''
    Fallback converter when nothing else matches:
        '', None convert to parameter default
        Anything else is returned as-is
    '''
    return _check_default(value, parameter, ( '', None ))


###  str (a passthrough)  ###

@parameter_converter(str)
def convert_str(value, parameter):
    '''
    Converts to string:
        '', None convert to parameter default
        Anything else is returned as-is (url params are already strings)
    '''
    return _check_default(value, parameter, ( '', None ))


###  int  ###

@parameter_converter(int)
def convert_int(value, parameter):
    '''
    Converts to int or float:
        '', '-', None convert to parameter default
        Anything else uses int() or float() constructor
    '''
    value = _check_default(value, parameter, ( '', '-', None ))
    if value is None or isinstance(value, int):
        return value
    try:
        return int(value)
    except Exception as e:
        raise ValueError(str(e))


###  float  ###

@parameter_converter(float)
def convert_float(value, parameter):
    '''
    Converts to int or float:
        '', '-', None convert to parameter default
        Anything else uses int() or float() constructor
    '''
    value = _check_default(value, parameter, ( '', '-', None ))
    if value is None or isinstance(value, float):
        return value
    try:
        return float(value)
    except Exception as e:
        raise ValueError(str(e))


###  decimal.Decimal  ###

@parameter_converter(decimal.Decimal)
def convert_decimal(value, parameter):
    '''
    Converts to decimal.Decimal:
        '', '-', None convert to parameter default
        Anything else uses Decimal constructor
    '''
    value = _check_default(value, parameter, ( '', '-', None ))
    if value is None or isinstance(value, decimal.Decimal):
        return value
    try:
        return decimal.Decimal(value)
    except Exception as e:
        raise ValueError(str(e))


###  bool  ###

@parameter_converter(bool)
def convert_boolean(value, parameter, default=False):
    '''
    Converts to boolean (only the first char of the value is used):
        '', '-', None convert to parameter default
        'f', 'F', '0', False always convert to False
        Anything else converts to True.
    '''
    value = _check_default(value, parameter, ( '', '-', None ))
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and len(value) > 0:
        value = value[0]
    return value not in ( 'f', 'F', '0', False, None )


###  datetime.datetime  ###

@parameter_converter(datetime.datetime)
def convert_datetime(value, parameter):
    '''
    Converts to datetime.datetime:
        '', '-', None convert to parameter default
        The first matching format in settings.DATETIME_INPUT_FORMATS converts to datetime
    '''
    value = _check_default(value, parameter, ( '', '-', None ))
    if value is None or isinstance(value, datetime.datetime):
        return value
    for fmt in settings.DATETIME_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    raise ValueError("`{}` does not match a format in settings.DATETIME_INPUT_FORMATS".format(value))


###   datetime.date  ###

@parameter_converter(datetime.date)
def convert_date(value, parameter):
    '''
    Converts to datetime.date:
        '', '-', None convert to parameter default
        The first matching format in settings.DATE_INPUT_FORMATS converts to datetime
    '''
    value = _check_default(value, parameter, ( '', '-', None ))
    if value is None or isinstance(value, datetime.date):
        return value
    for fmt in settings.DATE_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(value, fmt).date()
        except (ValueError, TypeError):
            continue
    raise ValueError("`{}` does not match a format in settings.DATE_INPUT_FORMATS".format(value))


###   Model: any Django model by its id  ###

@parameter_converter(Model)  # django models.Model
def convert_id_to_model(value, parameter):
    '''
    Converts to a Model object.
        '', '-', '0', None convert to parameter default
        Anything else is assumed an object id and sent to `.get(id=value)`.
    '''
    value = _check_default(value, parameter, ( '', '-', '0', None ))
    if isinstance(value, (int, str)):  # only convert if we have the id
        try:
            return parameter.type.objects.get(id=value)
        except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
            raise ValueError(str(e))
    return value



###################################
###   Helpers

def _check_default(value, parameter, default_chars):
    '''Returns the default if the value is "empty"'''
    # not using a set here because it fails when value is unhashable
    if value in default_chars:
        if parameter.default is inspect.Parameter.empty:
            raise ValueError('Value was empty, but no default value is given in view function for parameter: {} ({})'.format(parameter.position, parameter.name))
        return parameter.default
    return value
