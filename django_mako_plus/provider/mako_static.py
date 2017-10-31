from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist

from ..util import get_dmp_instance, merge_dicts
from .base import BaseProvider

import os
import os.path

try:
    from rjsmin import jsmin
except ImportError:
    jsmin = None
try:
    from rcssmin import cssmin
except ImportError:
    cssmin = None



###  DEPRECATED as of DMP 4.3.1
class MakoCssProvider(BaseProvider):
    '''Provides the content for *.cssm files'''
    default_options = merge_dicts(BaseProvider.default_options, {  
        'group': 'styles',
        'minify': True,
    })
    def init(self):
        self.cssm_dir = os.path.join(self.app_dir, 'styles')
        try:
            self.template = get_dmp_instance().get_template_loader_for_path(self.cssm_dir).get_template(self.template_name + '.cssm')
        except TemplateDoesNotExist:
            self.template = None
        
    def get_content(self, provider_run):
        if self.template is not None:
            content = self.template.render(request=provider_run.request, context=provider_run.context)
            if self.options['minify']:
                if cssmin is not None:
                    content = cssmin(content)
                else:
                    raise ImproperlyConfigured("Unable to minify {}.cssm because rcssmin is not available. Please `pip install rcssmin`.".format(self.template_name))
            return '<style type="text/css">{}</style>'.format(content)
        return None
        

###  DEPRECATED as of DMP 4.3.1
class MakoJsProvider(BaseProvider):
    '''Provides the content for *.jsm files'''
    default_options = merge_dicts(BaseProvider.default_options, {  
        'group': 'scripts',
        'minify': True,
    })
    def init(self):
        self.cssm_dir = os.path.join(self.app_dir, 'scripts')
        try:
            self.template = get_dmp_instance().get_template_loader_for_path(self.cssm_dir).get_template(self.template_name + '.jsm')
        except TemplateDoesNotExist:
            self.template = None
        
    def get_content(self, provider_run):
        if self.template is not None:
            content = self.template.render(request=provider_run.request, context=provider_run.context)
            if self.options['minify']:
                if jsmin is not None:
                    content = jsmin(content)
                else:
                    raise ImproperlyConfigured("Unable to minify {}.jsm because rjsmin is not available. Please `pip install rjsmin`.".format(self.template_name))
            return '<script type="text/javascript">{}</script>'.format(content)
        return None


