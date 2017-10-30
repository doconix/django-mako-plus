from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from ..util import DMP_OPTIONS, merge_dicts
from . import DEFAULT_STATIC_FILE_PROVIDERS

import os
import os.path



##################################################
###   Static File Provider Factory

def init_providers():
    '''Called when the DMP template engine is created by Django'''
    DMP_OPTIONS['RUNTIME_STATIC'] = [ ProviderFactory(provider_def) for provider_def in DMP_OPTIONS.get('STATIC_FILE_PROVIDERS', DEFAULT_STATIC_FILE_PROVIDERS) ]
    DMP_OPTIONS['RUNTIME_STATIC'].sort(key=lambda pf: pf.options['weight'], reverse=True)


class ProviderFactory(object):
    '''Creator for a given Provider definition in settings.py.'''
    def __init__(self, provider_def):
        self.options = {}
        try:
            self.provider_class = provider_def['provider']
        except KeyError:
            raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py; a STATIC_FILE_PROVIDERS item is missing `provider`.')
        if isinstance(self.provider_class, str):
            self.provider_class = import_string(self.provider_class)
        if not issubclass(self.provider_class, BaseProvider):
            raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py; The `provider` value must be a subclass of django_mako_plus.BaseProvider.')
        self.options = merge_dicts(self.provider_class.default_options, provider_def)
        
    def __call__(self, app_dir, template_name, cgi_id):
        return self.provider_class(app_dir, template_name, self.options, cgi_id)
        
        

##############################################################
###   Static File Providers

class BaseProvider(object):
    '''
    A list of providers is attached to each template as it is process.
    These are cached with the template, so .__init__() is only called once
    per system runtime, while .append_static() is called for each
    request.  Optimize the methods accordingly.
    '''
    default_options = {
        'group': 'styles',
        'weight': 0,  # higher weights run first
    }
    def __init__(self, app_dir, template_name, options, cgi_id):
        self.app_dir = app_dir
        self.template_name = os.path.splitext(template_name)[0]  # remove its extension
        self.options = dict(self.default_options)
        self.options.update(options)
        self.cgi_id = cgi_id
        self.init()
        
    @property
    def group(self):
        return self.options['group']

    def init(self):
        '''Called once when the template info obect is created.'''
        pass
        
    def append_static(self, request, context, html):
        '''Called each time the template renders.  Should return a string to be included in the HTML output.'''
        pass