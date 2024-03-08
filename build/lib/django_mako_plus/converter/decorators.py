from .base import ParameterConverter

###  Decorator that denotes a converter function  ###

def parameter_converter(*convert_types):
    '''
    Decorator that denotes a function as a url parameter converter.
    '''
    def inner(func):
        for ct in convert_types:
            ParameterConverter._register_converter(func, ct)
        return func
    return inner
