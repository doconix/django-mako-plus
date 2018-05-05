from django_mako_plus.converter import ParameterConverter
from django_mako_plus import view_function
from django.http import HttpRequest


class RecordingConverter(ParameterConverter):
    '''Converter that also records the converted variables for inspecting during testing'''
    def convert_parameters(self, *args, **kwargs):
        # request is usually args[0], but it can be args[1] when using functools.partial in the decorator
        request = args[1] if len(args) >= 2 and isinstance(args[1], HttpRequest) else args[0]
        args, kwargs = super().convert_parameters(*args, **kwargs)
        request.dmp.converted_params = kwargs
        return args, kwargs


class recording_view_function(view_function):
    '''View function decorator that uses the recording converter'''
    converter_class = RecordingConverter
