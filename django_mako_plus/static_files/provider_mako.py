from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist

from ..util import get_dmp_instance, merge_dicts
from .provider_base import BaseProvider

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
        'minify': True,
    })
    def init(self):
        self.cssm_dir = os.path.join(self.app_dir, 'styles')
        try:
            self.template = get_dmp_instance().get_template_loader_for_path(self.cssm_dir).get_template(self.template_name + '.cssm')
        except TemplateDoesNotExist:
            self.template = None
        
    def append_static(self, request, context, html):
        if self.template is not None:
            content = self.template.render(request=request, context=context)
            if self.options['minify']:
                if cssmin is not None:
                    content = cssmin(content)
                else:
                    raise ImproperlyConfigured("Unable to minify {}.cssm because rcssmin is not available. Please `pip install rcssmin`.".format(self.template_name))
            html.append('<style type="text/css">{}</style>'.format(content))
        

###  DEPRECATED as of DMP 4.3.1
class MakoJsProvider(BaseProvider):
    '''Provides the content for *.jsm files'''
    default_options = merge_dicts(BaseProvider.default_options, {  
        'minify': True,
    })
    def init(self):
        self.cssm_dir = os.path.join(self.app_dir, 'scripts')
        try:
            self.template = get_dmp_instance().get_template_loader_for_path(self.cssm_dir).get_template(self.template_name + '.jsm')
        except TemplateDoesNotExist:
            self.template = None
        
    def append_static(self, request, context, html):
        if self.template is not None:
            content = self.template.render(request=request, context=context)
            if self.options['minify']:
                if jsmin is not None:
                    content = jsmin(content)
                else:
                    raise ImproperlyConfigured("Unable to minify {}.jsm because rjsmin is not available. Please `pip install rjsmin`.".format(self.template_name))
            html.append('<script type="text/javascript">{}</script>'.format(content))


