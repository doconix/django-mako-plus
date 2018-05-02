from .system import _check_converter


##################################################################
###   ConversionTask object

class ConversionTask(object):
    '''
    A (mostly) data class that holds meta-information about a conversion
    task.  This object is sent into each converter function.
    '''
    def __init__(self, request, module, function, view_function_kwargs):
        # view_function_kwargs are from the @view_function(k1=v1, k2=v2)
        self.converter = _check_converter(view_function_kwargs.get('converter'))
        self.request = request
        self.module = module
        self.function = function
        self.view_function_kwargs = view_function_kwargs


    def convert_value(self, value, parameter):
        '''Converts a value using the converters specified in the @view_function decorator'''
        try:


        except BaseRedirectException as e:
            log.info('Redirect exception raised during conversion of parameter %s (%s): %s', parameter.position, parameter.name, e)
            raise

        except Http404 as e:
            log.info('Raising Http404 because exception raised during conversion of parameter %s (%s): %s', parameter.position, parameter.name, e, exc_info=e)
            raise

        except Exception as e:
            log.info('Exception raised during conversion of parameter %s (%s): %s', parameter.position, parameter.name, e, exc_info=e)
            handler = ctask.view_function_kwargs.get('converter_error')
            if callable(handler):
                kwargs[parameter.name] =
            raise Http404('Invalid parameter specified in the url')
