
import functools


##########################################################
###   An extensible decorator superclass that supports:
###       - Calling without any arguments
###       - Calling with empty args
###       - Calling with args and keyword args
###       - Decorating regular functions
###       - Decorating class methods
###
###   Author: Conan Albrecht <doconix@gmail.com>
###   Date: 2018-05-05
###
###   See the examples at the end of this file.
###


class BaseDecoratorMeta(type):
    '''
    Metaclass that allows ourdecorator to be called
    with or without optional arguments.
    '''
    def __call__(self, *args, **kwargs):
        # if args has a single function, we'll assume it is the function we're decorating.
        # that means the syntax was `@decorator` or `@decorator()` -- no arguments
        # we need to return normally
        if len(args) == 1 and callable(args[0]):
            instance = super(BaseDecoratorMeta, self).__call__(*args, **kwargs)
            functools.update_wrapper(instance, args[0])
            return instance

        # if we get here, the syntax was `@decorator(a=1, b=2)` -- with arguments
        # python hasn't yet "called" the decorator.  we'll return a factory
        # for python to call with the decorated function
        def factory(func):
            instance = super(BaseDecoratorMeta, self).__call__(func, *args, **kwargs)
            functools.update_wrapper(instance, func)
            return instance
        return factory


class BaseDecorator(object, metaclass=BaseDecoratorMeta):
    '''
    A decorator that can be called with an arbitrary number of
    arguments and keyword arguments.
    '''
    def __init__(self, decorator_function, *decorator_args, **decorator_kwargs):
        self.decorator_function = decorator_function
        self.decorator_args = decorator_args
        self.decorator_kwargs = decorator_kwargs

    def __get__(self, instance, type=None):
        # If we get here, the decorator was placed on a class method.  In this case,
        # decorated_function is actually an unbound function not yet a bound method.
        # Python calls this descriptor when the method is called.
        # When it does so, we need to set the self variable so it gets "bound".
        return functools.partial(self, instance)

    def __call__(self, *args, **kwargs):
        '''Subclasses should override this method'''
        return self.decorator_function(*args, **kwargs)



#######################################################
###   Examples and Simple Testing


def __test__():

    class my_decorator(BaseDecorator):
        def __call__(self, *args, **kwargs):
            # do something useful here
            print('--')
            print('func:  ', self.decorator_function.__name__, '({})'.format(self.decorator_function))
            print('args:  ', self.decorator_args)
            print('kwargs:', self.decorator_kwargs)

            # finally, call the decorated function
            return self.decorator_function(*args, **kwargs)


    ###  Decorating Functions  ###

    @my_decorator
    def without_args():
        print('without_args() called')

    @my_decorator()
    def with_empty_args():
        print('with_empty_args() called')

    @my_decorator(1, 2, 3)
    def with_args():
        print('with_args() called')

    @my_decorator(option1='value1', option2=4)
    def with_kwargs():
        print('with_kwargs() called')

    @my_decorator(1, 2, 3, option1='value1', option2=4)
    def with_args_and_kwargs():
        print('with_args_and_kwargs() called')

    print('\n\nRegular Functions:\n')
    without_args()
    with_empty_args()
    with_args()
    with_kwargs()
    with_args_and_kwargs()


    ###  Decorating Class Methods  ###

    class MyClass(object):
        @my_decorator
        def without_args(self):
            print('class method without_args() called')

        @my_decorator()
        def with_empty_args(self):
            print('class method with_empty_args() called')

        @my_decorator(1, 2, 3)
        def with_args(self):
            print('class method with_args() called')

        @my_decorator(option1='value1', option2=4)
        def with_kwargs(self):
            print('class method with_kwargs() called')

        @my_decorator(1, 2, 3, option1='value1', option2=4)
        def with_args_and_kwargs(self):
            print('class method with_args_and_kwargs() called')

    print('\n\nClass Methods:\n')
    my_class = MyClass()
    my_class.without_args()
    my_class.with_empty_args()
    my_class.with_args()
    my_class.with_kwargs()
    my_class.with_args_and_kwargs()


    ###  Invalid  ###

    # the only decorator syntax not supported is a single function value becaus
    # because python thinks it's the decorated function when it's actually meant
    # to be the pre-decorator call.
    print('\n\nInvalid:\n')
    try:
        @my_decorator(sum)
        def with_single_callable():
            print('with_single_callable() called')
    except Exception as e:
        print("Invalid syntax: can't determine whether to decorate the `sum` function or the `with_single_callable` function")



if __name__ == '__main__':
    __test__()
