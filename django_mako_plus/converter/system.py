from ..util import DMP_OPTIONS
from .base import BaseConverter
from .default import DefaultConverter

import inspect


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
