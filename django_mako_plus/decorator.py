
import functools

##########################################################
###   An extensible decorator superclass that supports:
###       1. @mydecorator
###       2. @mydecorator()
###       3. @mydecorator(1, 2, 3)
###       4. @mydecorator(a=1, b=2)
###       5. @mydecorator(1, 2, 3, a=1, b=2)
###
###       AND
###
###       A. It works on regular functions.
###       B. It works on unbound class methods.
###       C. It works on bound class methods.
###
###   Author: Conan Albrecht <doconix@gmail.com>
###   Date: 2018-05-05
###
###   See the examples at the end of this file.
###
###   The reason I argue for a metaclass approach:
###
###   When a decorator is hit by python, it either 1) needs to call the decorator function with the
###   other function, or 2) if arguments, run the decorator pre-function, which returns the real decorator,
###   and then #1 with that.
###
###   So in other words, the decorator needs to act like two entirely separate things.  Since a metaclass’
###   job is to create the object, it seems a clean approach to have the metaclass create the right kind
###   of thing needed.
###
###   Since this decision is being made *before* the decorator is created, the decorator class itself
###   can act as just one type of object: a decorator.  The decorator’s `__init__` constructor is super
###   clean because it doesn’t have to check whether we’re in pre-decorator or regular decorator mode.
###   If the decorator constructor is running, it *is decorating* a function.
###

class BaseDecoratorMeta(type):
    '''
    Metaclass that either creates the decorator object or creates a
    factory to create the decorator object.
    '''
    def __call__(self, *args, **kwargs):
        # if args has a single function, we'll assume it is the function we're decorating.
        # that means the syntax was `@decorator` -- no arguments, so
        # we need to return normally.
        if len(args) == 1 and callable(args[0]) and len(kwargs) == 0:
            instance = super(BaseDecoratorMeta, self).__call__(*args, **kwargs)
            functools.update_wrapper(instance, args[0])
            return instance

        # if we get here, the syntax was `@decorator(...)` -- with arguments.
        # python hasn't yet "called" the decorator.  we'll return a factory
        # for python to call with the decorated function
        def factory(func):
            instance = super(BaseDecoratorMeta, self).__call__(func, *args, **kwargs)
            functools.update_wrapper(instance, func)
            return instance
        return factory


class BaseDecorator(object, metaclass=BaseDecoratorMeta):
    '''
    A decorator base class that can be called with an arbitrary number of
    arguments and keyword arguments, or with none at all.
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

if __name__ == '__main__':

    import unittest

    ###  Our Decorator  ###

    class my_decorator(BaseDecorator):
        def __call__(self, *args, **kwargs):
            # do something useful here (the purpose of the decorator)

            # call the decorated function
            result = self.decorator_function(*args, **kwargs)

            # return some things to be tested
            return self, result


    ###  Examples and Tests of Regular Function Decorating  ###

    @my_decorator
    def without_args():
        return 'without_args called'

    @my_decorator()
    def with_empty_args():
        return 'with_empty_args called'

    @my_decorator(1, 2, 3)
    def with_args():
        return 'with_args called'

    @my_decorator(option1='value1', option2=4)
    def with_kwargs():
        return 'with_kwargs called'

    @my_decorator(1, 2, 3, option1='value1', option2=4)
    def with_args_and_kwargs():
        return 'with_args_and_kwargs called'

    class TestFunctionDecorating(unittest.TestCase):
        def test_without_args(self):
            '''Decorating without any arguments or parenthasis'''
            dec, result = without_args()
            self.assertEqual(result, 'without_args called')
            self.assertEqual(dec.decorator_args, ())
            self.assertEqual(dec.decorator_kwargs, {})

        def test_with_empty_args(self):
            '''Decorating with empty arguments'''
            dec, result = with_empty_args()
            self.assertEqual(result, 'with_empty_args called')
            self.assertEqual(dec.decorator_args, ())
            self.assertEqual(dec.decorator_kwargs, {})

        def test_with_args(self):
            '''Decorating with positional arguments'''
            dec, result = with_args()
            self.assertEqual(result, 'with_args called')
            self.assertEqual(dec.decorator_args, (1, 2, 3))
            self.assertEqual(dec.decorator_kwargs, {})

        def test_with_kwargs(self):
            '''Decorating with positional arguments'''
            dec, result = with_kwargs()
            self.assertEqual(result, 'with_kwargs called')
            self.assertEqual(dec.decorator_args, ())
            self.assertEqual(dec.decorator_kwargs, { 'option1':'value1', 'option2':4 })

        def test_with_args_and_kwargs(self):
            '''Decorating with positional arguments'''
            dec, result = with_args_and_kwargs()
            self.assertEqual(result, 'with_args_and_kwargs called')
            self.assertEqual(dec.decorator_args, (1, 2, 3))
            self.assertEqual(dec.decorator_kwargs, { 'option1':'value1', 'option2':4 })


    ###  Examples and Tests of Method Decorating  ###

    class MyTestClass(object):
        @my_decorator
        def without_args(self):
            return 'without_args called'

        @my_decorator()
        def with_empty_args(self):
            return 'with_empty_args called'

        @my_decorator(1, 2, 3)
        def with_args(self):
            return 'with_args called'

        @my_decorator(option1='value1', option2=4)
        def with_kwargs(self):
            return 'with_kwargs called'

        @my_decorator(1, 2, 3, option1='value1', option2=4)
        def with_args_and_kwargs(self):
            return 'with_args_and_kwargs called'

    class TestMethodDecorating(unittest.TestCase):

        def setUp(self):
            self.my_test_class = MyTestClass()

        def test_without_args(self):
            '''Decorating without any arguments or parenthasis'''
            dec, result = self.my_test_class.without_args()
            self.assertEqual(result, 'without_args called')
            self.assertEqual(dec.decorator_args, ())
            self.assertEqual(dec.decorator_kwargs, {})

        def test_with_empty_args(self):
            '''Decorating with empty arguments'''
            dec, result = self.my_test_class.with_empty_args()
            self.assertEqual(result, 'with_empty_args called')
            self.assertEqual(dec.decorator_args, ())
            self.assertEqual(dec.decorator_kwargs, {})

        def test_with_args(self):
            '''Decorating with positional arguments'''
            dec, result = self.my_test_class.with_args()
            self.assertEqual(result, 'with_args called')
            self.assertEqual(dec.decorator_args, (1, 2, 3))
            self.assertEqual(dec.decorator_kwargs, {})

        def test_with_kwargs(self):
            '''Decorating with positional arguments'''
            dec, result = self.my_test_class.with_kwargs()
            self.assertEqual(result, 'with_kwargs called')
            self.assertEqual(dec.decorator_args, ())
            self.assertEqual(dec.decorator_kwargs, { 'option1':'value1', 'option2':4 })

        def test_with_args_and_kwargs(self):
            '''Decorating with positional arguments'''
            dec, result = self.my_test_class.with_args_and_kwargs()
            self.assertEqual(result, 'with_args_and_kwargs called')
            self.assertEqual(dec.decorator_args, (1, 2, 3))
            self.assertEqual(dec.decorator_kwargs, { 'option1':'value1', 'option2':4 })



    class TestInvalidSyntax(unittest.TestCase):

        def test_invalid_syntax(self):
            '''
            Invalid: the only decorator syntax not supported is a single function value
            because python thinks it's the decorated function when it's actually meant
            to be the pre-decorator call.
            '''
            with self.assertRaises(TypeError):
                # we can't tell wether to decorate `sum` or `with_single_callable` here:
                @my_decorator(sum)
                def with_single_callable():
                    print('with_single_callable() called')
                with_single_callable()

    # trigger the testing
    unittest.main()
