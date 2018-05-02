from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

import inspect
import sys




##################################################################
###   ConverterInfo class: see @convert_method below

class ConverterInfo(object):
    '''
    Used by @convert_method to track types on a converter method.
    '''
    CONVERT_TYPES_KEY = '_dmp_converter_infos'
    DECLARED_ORDER = 0

    def __init__(self, convert_type, convert_func):
        self.convert_type = convert_type
        self.convert_func = convert_func
        self.sort_key = None
        self.declared_order = ConverterInfo.DECLARED_ORDER  # order it was declared in source code
        ConverterInfo.DECLARED_ORDER = 0 if ConverterInfo.DECLARED_ORDER == sys.maxsize else ConverterInfo.DECLARED_ORDER + 1

    def _delayed_init(self):
        # we allow the type for models to be declared as a string, such as "auth.User"
        # because real types can't be referenced until Django finishes initialization
        # switch any strings over to the real type now
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
        self.sort_key = ( -1 * len(inspect.getmro(self.convert_type)), -1 * self.declared_order )
