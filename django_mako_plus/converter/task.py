from .system import _check_converter


##################################################################
###   ConversionTask object

class ConversionTask(object):
    '''
    A (mostly) data class that holds meta-information about a conversion
    task.  This object is sent into each converter function.
    '''
    def __init__(self, request, module, function, kwargs):
        # kwargs are from the @view_function(k1=v1, k2=v2) on the current view function
        # we are guaranteed to have key `converter` because it is in the
        # DEFAULT_KWARGS (see decorators.py)
        self.converter = _check_converter(kwargs.get('converter'))
        self.request = request
        self.module = module
        self.function = function
        self.kwargs = kwargs
