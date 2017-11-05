from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.encoding import force_text

from ..util import DMP_OPTIONS, merge_dicts

import os
import os.path



##################################################
###   Static File Provider Factory


DEFAULT_CONTENT_PROVIDERS = [
    { 'provider': 'django_mako_plus.CssLinkProvider' },
    { 'provider': 'django_mako_plus.JsLinkProvider'  },
    # deprecated as of Oct 2017
    { 'provider': 'django_mako_plus.MakoCssProvider'  },
    { 'provider': 'django_mako_plus.MakoJsProvider'  },
]


def init_providers():
    '''Called when the DMP template engine is created by Django'''
    DMP_OPTIONS['RUNTIME_PROVIDERS'] = [ ProviderFactory(provider_def) for provider_def in DMP_OPTIONS.get('CONTENT_PROVIDERS', DEFAULT_CONTENT_PROVIDERS) ]
    DMP_OPTIONS['RUNTIME_PROVIDERS'].sort(key=lambda pf: pf.options['weight'], reverse=True)


class ProviderFactory(object):
    '''Creator for a given Provider definition in settings.py.'''
    def __init__(self, provider_def):
        self.options = {}
        try:
            self.provider_class = provider_def['provider']
        except KeyError:
            raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py; a CONTENT_PROVIDERS item is missing `provider`.')
        if isinstance(self.provider_class, str):
            self.provider_class = import_string(self.provider_class)
        if not issubclass(self.provider_class, BaseProvider):
            raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py; The `provider` value must be a subclass of django_mako_plus.BaseProvider.')
        self.options = merge_dicts(self.provider_class.default_options, provider_def)
        
    def create(self, app_dir, template_name, version_id):
        return self.provider_class(app_dir, template_name, self.options, version_id)
        
        

##############################################################
###   Static File Providers

class BaseProvider(object):
    '''
    A list of providers is attached to each template as it is process.
    These are cached with the template, so .__init__() is only called once
    per system runtime, while .append_content() is called for each
    request.  Optimize the methods accordingly.
    '''
    default_options = {
        'group': 'styles',
        'weight': 0,  # higher weights run first
    }
    def __init__(self, app_dir, template_name, options, version_id):
        self.app_name = os.path.split(app_dir)[1]                  # django app name
        self.app_dir = app_dir                                     # absolute path
        self.template_name = os.path.splitext(template_name)[0]    # without the extension
        self.options = merge_dicts(self.default_options, options)  # combined options dictionary
        self.version_id = version_id                               # unique number for overriding the cache (see LinkProvider)
        self.init()
        
        
    @property
    def group(self):
        return self.options['group']


    def init(self):
        '''Called at the end of the constructor.'''
        
        
    def get_content(self, provider_run):
        '''
        Called each time the template renders.  Should return a string 
        to be included in the HTML output, or None if no content.
        '''
        return None
        
        
    def format_string(self, val):
        '''
        Helper function that runs st.format with some standard named options.
        val.format() is called with {appname}, {appdir}, {template}.
        '''
        return force_text(val).format(
            appname=self.app_name,
            appdir=self.app_dir,
            template=self.template_name,
        )
        