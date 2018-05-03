import functools


class OptionsDecoratorMeta(type):
    '''
    Metaclass that allows ourdecorator to be called
    with or without optional arguments.
    '''
    def __call__(self, *args, **kwargs):
        # if args has a single function, we'll assume it is the function we're decorating.
        # that means the syntax was `@decorator` or `@decorator()` -- no arguments
        # we need to return normally
        if len(args) == 1 and callable(args[0]):
            instance = super(OptionsDecoratorMeta, self).__call__(*args, **kwargs)
            functools.update_wrapper(instance, args[0])
            return instance

        # if we get here, the syntax was `@decorator(a=1, b=2)` -- with arguments
        # python hasn't yet "called" the decorator.  we'll return a factory
        # for python to call with the function
        def factory(func):
            instance = super(OptionsDecoratorMeta, self).__call__(func, *args, **kwargs)
            functools.update_wrapper(instance, func)
            return instance
        return factory


class OptionsDecorator(object, metaclass=OptionsDecoratorMeta):
    '''
    A class-based decorator that can be called with or without options (kwargs):

        @decorator
        @decorator()
        @decorator(option1=value1, option2=value2)

    Override the __call__() method for custom behavior.
    '''
    def __init__(self, decorated_function, **options):
        '''Create a new wrapper around the decorated function'''
        self.decorated_function = decorated_function
        self.options = options


    def __call__(self, *args, **kwargs):
        '''Subclasses should override this method'''
        return self.decorated_function(*args, **kwargs)
