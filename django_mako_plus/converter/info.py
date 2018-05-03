from django.apps import apps
from django.core.exceptions import ImproperlyConfigured


import inspect
import sys



class ConverterFunctionInfo(object):
    '''Holds information about a converter function'''
    def __init__(self, convert_func, convert_type, source_order):
        self.convert_func = convert_func
        self.convert_type = convert_type
        self.source_order = source_order
        self.sort_key = 0


    def prepare_sort_key(self):
        '''
        Triggered by view_function._sort_converters when our sort key should be created.
        This can't be called in the constructor because Django models might not be ready yet.
        '''
        if isinstance(self.convert_type, str):
            try:
                app_name, model_name = self.convert_type.split('.')
            except ValueError:
                raise ImproperlyConfigured('"{}" is not a valid converter type. String-based converter types must be specified in "app.Model" format.'.format(self.convert_type))
            try:
                self.convert_type = apps.get_model(app_name, model_name)
            except LookupError as e:
                raise ImproperlyConfigured('"{}" is not a valid model name. {}'.format(self.convert_type, e))

        # we reverse sort by ( len(mro), source code order ) so subclasses match first
        # on same types, last declared method sorts first
        self.sort_key = ( -1 * len(inspect.getmro(self.convert_type)), -1 * self.source_order )
