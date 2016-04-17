from django.apps import apps, AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist, engines
from django.template.backends.base import BaseEngine
from django.utils.module_loading import import_string

from mako.template import Template

from .exceptions import InternalRedirectException, RedirectException
from .signals import dmp_signal_pre_render_template, dmp_signal_post_render_template, dmp_signal_redirect_exception
from .template import MakoTemplateLoader, MakoTemplateAdapter
from .util import DMP_INSTANCE, get_dmp_instance, get_dmp_option, get_dmp_app_configs, log

from copy import deepcopy
import os, os.path, sys



#########################################################
###   The main engine

class MakoTemplates(BaseEngine):
    '''The primary Mako interface that plugs into the Django templating system.
       This is referenced in settings.py -> TEMPLATES.
    '''
    def __init__(self, params):
        '''Constructor'''
        # cache our instance in the util module for get_dmp_instance
        # this is a bit of a hack, but it makes calling utility methods possible
        DMP_INSTANCE[0] = self

        # pop off the params - we deep copy these so we don't modify the settings
        self.options = deepcopy(params)
        try:
            self.options.update(params.pop('OPTIONS'))
        except KeyError:
            raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py.  Please ensure the OPTIONS is set in the template setup.')

        # super constructor
        super(MakoTemplates, self).__init__(params)

        # set up the context processors
        context_processors = []
        for processor in self.options.get('CONTEXT_PROCESSORS', []):
            context_processors.append(import_string(processor))
        self.template_context_processors = tuple(context_processors)

        # add a template renderer for each DMP-enabled app
        self.template_loaders = {}
        for app_config in get_dmp_app_configs():
            self.register_app(app_config)


    def register_app(self, app_config):
        '''Registers an app as a "DMP-enabled" app.  Registering creates a cached
           template renderer to make processing faster and adds the dmp_render()
           and dmp_render_to_string() methods to the app.  When Django starts,
           this method is called automatically for any app with
           DJANGO_MAKO_PLUS = True in its __init__.py file.

           This method should not normally be called directly.
        '''
        # set up the template, script, and style renderers
        self.get_template_loader(app_config, 'templates', create=True)
        self.get_template_loader(app_config, 'scripts', create=True)
        self.get_template_loader(app_config, 'styles', create=True)

        # add the shortcut functions (only to the main templates, we don't do to scripts or styles
        # because people generally don't call those directly).  This is a monkey patch, but it is
        # an incredibly useful one because it makes calling app-specific rendering functions much
        # easier.
        #
        # Django's shortcut to return an *HttpResponse* is render(), and its template method to render a *string* is also render().
        # Good job on naming there, folks.  That's going to confuse everyone.  But I'm matching it to be consistent despite the potential confusion.
        app_config.module.dmp_render = RenderShortcut(self, app_config.name, 'render_to_response')   # the Django shortcut to return an HttpResponse is render().
        app_config.module.dmp_render_to_string = RenderShortcut(self, app_config.name, 'render')  # the Django Template method to render to a string is render().  Django templates never return a direct response.


    def from_string(self, template_code):
        '''Compiles a template from the given string.
           This is one of the required methods of Django template engines.
        '''
        mako_template = Template(template_code, imports=get_dmp_option('DEFAULT_TEMPLATE_IMPORTS'), input_encoding=get_dmp_option('DEFAULT_TEMPLATE_ENCODING', 'utf-8'))
        return MakoTemplateAdapter(mako_template)


    def get_template(self, template_name):
        '''Retrieves a template object.
           This is one of the required methods of Django template engines.

           Because DMP templates are always app-specific (Django only searches
           a global set of directories), the template_name MUST be in the format:
           "app_name/template.html".  DMP splits the template_name string on the
           slash to get the app name and template name.

           Only forward slashes are supported.  Use / even on Windows to specify
           the "app_name/template.html".
        '''
        parts = template_name.split('/', 1)
        if len(parts) < 2:
            raise TemplateDoesNotExist('Invalid template_name format for a DMP template.  This method requires that the template name be in app_name/template.html format (separated by slash).')
        return self.get_template_loader(parts[0]).get_template('/'.join(parts[1:]))


    def get_template_loader(self, app, subdir='templates', create=False):
        '''
        Returns a template loader object for the given app name in the given subdir.
        For example, get_template_loader('homepage', 'styles') will return
        a loader for the styles/ directory in the homepage app.

        The app parameter can be either an app name or an AppConfig instance.
        The subdir parameter is normally 'templates', 'scripts', or 'styles',
        but it can be any subdirectory name of the given app.

        Normally, you should not have to call this method.  Django automatically
        generates two shortcut functions for every DMP-registered app (apps with
        DJANGO_MAKO_PLUS = True), and these shortcut functions are the preferred
        way to render templates.

        This method is useful when you want a custom template loader to a directory
        that does not conform to the app_dir/templates/* pattern.

        If the loader is not found in the DMP cache, one of two things occur:
          1. If create=True, it is created automatically and returned.  This overrides
             the need to set DJANGO_MAKO_PLUS=True in the app's __init__.py file.
          2. If create=False, a TemplateDoesNotExist is raised.  This is the default
             behavior.
        '''
        # ensure we have an AppConfig
        if not isinstance(app, AppConfig):
            app = apps.get_app_config(app)

        # get the loader with the path of this app+subdir
        path = os.path.join(app.path, subdir)

        # if create=False, the loader must already exist in the cache
        if not create and path not in self.template_loaders:
            raise TemplateDoesNotExist("%s has not been registered as a DMP app.  Did you forget to include the DJANGO_MAKO_PLUS=True line in your app's __init__.py?" % app.name)

        # return the template by path
        return self.get_template_loader_for_path(path, use_cache=True)


    def get_template_loader_for_path(self, path, use_cache=True):
        '''
        Returns a template loader object for the given directory path.
        For example, get_template_loader('/var/mytemplates/') will return
        a loader for that specific directory.

        Normally, you should not have to call this method.  Django automatically
        generates two shortcut functions for every DMP-registered app (apps with
        DJANGO_MAKO_PLUS = True), and these shortcut functions are the preferred
        way to render templates.

        This method is useful when you want a custom template loader for a specific
        directory that may be outside your project directory or that is otherwise
        not contained in a normal Django app.  If the directory is inside an app,
        call get_template_loader() instead.

        Unless use_cache=False, this method caches template loaders in the DMP
        cache for later use.
        '''
        # get from the cache if we are able
        if use_cache:
            try:
                return self.template_loaders[path]
            except KeyError:
                pass  # not there, so we'll create

        # create the loader
#        print('>>>>>>>> creating loader', path)
        loader = MakoTemplateLoader(path, None)

        # cache if we are allowed
        if use_cache:
            self.template_loaders[path] = loader

        # return
        return loader



class RenderShortcut(object):
    '''A shortcut way to call render() on a template.
       This enables the primary DMP way to run templates.
       These shortcuts are created in MakoTemplates.__init__ above.
       Use of these shortcuts:

         # this code goes in an app's view files, such as views/index.py
         from .. import render, render_to_string

         # to render templates/index.html to a string
         st = render_to_string(request, 'index.html', { 'var1': 'value' })

         # to render templates/index.html to an HttpResponse
         response = render(request, 'index.html', { 'var1': 'value' })

         # this shows how to render a file in a scripts/ or styles/ folder
         # to render scripts/index.jsm to a string
         st = render_to_string(request, 'index.html', { 'var1': 'value' }, subdir='scripts')

         # to render styles/index.cssm to a response
         response = render(request, 'index.html', { 'var1': 'value' }, subdir='styles')

         # to render a specific "def" block within a template (see Mako documentation for defs)
         response = render(request, 'index.html', { 'var1': 'value' }, def_name='myfunc')
    '''
    def __init__(self, dmp_instance, app_name, template_method_name):
        self.dmp_instance = dmp_instance
        self.app_name = app_name
        self.template_method_name = template_method_name


    def __call__(self, request, template, context=None, def_name=None, subdir='templates'):
        '''Allows instances of this class to act like functions.'''
        # I'm doing "late binding" to the map, just in
        # case new template loader objects are added after creation.
        # This way I don't have a direct (and permanent) pointer to the loader object.
        template_loader = self.dmp_instance.get_template_loader(self.app_name, subdir)
        template_obj = template_loader.get_template(template)
        return getattr(template_obj, self.template_method_name)(context=context, request=request, def_name=def_name)
