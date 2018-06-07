
#####################################
###  ViewParameter

class ViewParameter(object):
    '''
    A data class that represents a view parameter on a view function.
    An instance of this class is created for each parameter in a view function
    (except the initial request object argument).
    '''
    def __init__(self, name, position, kind, type, default):
        '''
        name:      The name of the parameter.
        position:  The position of this parameter.
        kind:      The kind of argument (positional, keyword, etc.). See inspect module.
        type:      The expected type of this parameter.  Converters use this type to
                   convert urlparam strings to the right type.
        default:   Any default value, specified in function type hints.  If no default is
                   specified in the function, this is `inspect.Parameter.empty`.
        '''
        self.name = name
        self.position = position
        self.kind = kind
        self.type = type
        self.default = default

    def __repr__(self):
        return '<ViewParameter name={}, type={}, default={}>'.format(
            self.name,
            self.type.__qualname__ if self.type is not None else '<not specified>',
            self.default,
        )
