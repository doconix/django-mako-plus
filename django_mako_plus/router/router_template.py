from ..util import get_dmp_instance
from .base import Router



class TemplateViewRouter(Router):
    '''Router for direct templates (used whe a view.py file doesn't exist but the .html does)'''
    def __init__(self, app_name, template_name):
        # not keeping the actual template objects because we need to get from the loader each time (Mako has its own cache)
        self.app_name = app_name
        self.template_name = template_name
        # check the template by loading it
        get_dmp_instance().get_template_loader(self.app_name).get_template(self.template_name)


    def get_response(self, request, *args, **kwargs):
        template = get_dmp_instance().get_template_loader(self.app_name).get_template(self.template_name)
        return template.render_to_response(request=request, context=kwargs)


    def message(self, request, descriptive=True):
        if descriptive:
            return 'template {} (view function {}.{} not found)'.format(self.template_name, request.dmp.module, request.dmp.function)
        return str(self.template_name)
