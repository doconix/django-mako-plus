from django.http import Http404
from .base import Router




class RegistryExceptionRouter(Router):
    '''Router for a registry exception (i.e. view not found).'''
    def __init__(self, exc):
        self.exc = exc


    def get_response(self, request, *args, **kwargs):
        raise Http404(str(self.exc))


    def message(self, request, descriptive=True):
        if descriptive:
            return 'RegistryExceptionRouter: {}'.format(self.exc)
        return str(self.exc)
