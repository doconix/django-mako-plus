from django.apps import apps, AppConfig
from django.conf import settings
from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist, engines, TemplateSyntaxError
from django.template.backends.base import BaseEngine
from django.utils.module_loading import import_string
from django.views.generic import View

from .exceptions import InternalRedirectException, RedirectException, DMPViewDoesNotExist
from .signals import dmp_signal_pre_render_template, dmp_signal_post_render_template, dmp_signal_redirect_exception
from .template import MakoTemplateLoader, MakoTemplateAdapter, TemplateViewFunction
from .util import get_dmp_instance, get_dmp_app_configs, log, DMP_OPTIONS, DMP_INSTANCE_KEY
from .util import DMP_VIEW_FUNCTION, DMP_VIEW_CLASS_METHOD

from mako.template import Template

from copy import deepcopy
from inspect import isclass
from importlib import import_module
from importlib.util import find_spec
import os, os.path, sys, itertools, threading, collections

try:
    # python 3.4+
    from importlib.util import find_spec
except ImportError:
    # python <= 3.3
    from importlib import find_loader as find_spec


# Following Django's lead, hard coding the CSRF processor
_builtin_context_processors = ('django_mako_plus.context_processors.csrf',)



#########################################################
###   The main engine

class MakoTemplates(BaseEngine):
    '''
    The primary Mako interface that plugs into the Django templating system.
    This is referenced in settings.py -> TEMPLATES.
    '''
    def __init__(self, params):
        '''Constructor'''
        # pop the settings.py options into the DMP options
        try:
            DMP_OPTIONS.update(params.pop('OPTIONS'))
        except KeyError:
            raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py.  Please ensure the OPTIONS is set in the template setup.')

        # cache our instance in the util module for get_dmp_instance
        # this is a bit of a hack, but it makes calling utility methods possible and efficient
        DMP_OPTIONS[DMP_INSTANCE_KEY] = self
        self.template_loaders = {}
        self.dmp_enabled_apps = set()
        self.view_cache = {}
        self.rlock = threading.RLock()

        # super constructor
        super(MakoTemplates, self).__init__(params)

        # set up the context processors
        context_processors = []
        for processor in itertools.chain(_builtin_context_processors, DMP_OPTIONS.get('CONTEXT_PROCESSORS', [])):
            context_processors.append(import_string(processor))
        self.template_context_processors = tuple(context_processors)

        # now that our engine has loaded, initialize a few parts of it
        # should we minify JS AND CSS FILES?
        DMP_OPTIONS['RUNTIME_JSMIN'] = False
        DMP_OPTIONS['RUNTIME_CSSMIN'] = False
        if DMP_OPTIONS.get('MINIFY_JS_CSS', False) and not settings.DEBUG:
            try:
                from rjsmin import jsmin
            except ImportError:
                raise ImproperlyConfigured('MINIFY_JS_CSS = True in the Django Mako Plus settings, but the "rjsmin" package does not seem to be loaded.')
            try:
                from rcssmin import cssmin
            except ImportError:
                raise ImproperlyConfigured('MINIFY_JS_CSS = True in the Django Mako Plus settings, but the "rcssmin" package does not seem to be loaded.')
            DMP_OPTIONS['RUNTIME_JSMIN'] = jsmin
            DMP_OPTIONS['RUNTIME_CSSMIN'] = cssmin

        # should we compile SASS files?
        DMP_OPTIONS['RUNTIME_SCSS_ENABLED'] = False
        SCSS_BINARY = DMP_OPTIONS.get('SCSS_BINARY', None)
        if isinstance(SCSS_BINARY, str):  # for backwards compatability
            log.warning('Future warning: the settings.py variable SCSS_BINARY should be a list of arguments, not a string.')
            DMP_OPTIONS['RUNTIME_SCSS_ARGUMENTS'] = SCSS_BINARY.split(' ')
            DMP_OPTIONS['RUNTIME_SCSS_ENABLED'] = True
        elif isinstance(SCSS_BINARY, (list, tuple)):
            DMP_OPTIONS['RUNTIME_SCSS_ARGUMENTS'] = SCSS_BINARY
            DMP_OPTIONS['RUNTIME_SCSS_ENABLED'] = True
        elif not SCSS_BINARY:
            DMP_OPTIONS['RUNTIME_SCSS_ARGUMENTS'] = None
        else:
            raise ImproperlyConfigured('The SCSS_BINARY option in Django Mako Plus settings must be a list of arguments.  See the DMP documentation.')

        # add a template renderer for each DMP-enabled app
        for app_config in get_dmp_app_configs():
            self.register_app(app_config)


    def register_app(self, app):
        '''
        Registers an app as a "DMP-enabled" app.  Registering creates a cached
        template renderer to make processing faster and adds the dmp_render()
        and dmp_render_to_string() methods to the app.  When Django starts,
        this method is called automatically for any app with
        DJANGO_MAKO_PLUS = True in its __init__.py file.

        app: The name of the app or an AppConfig instance.
        '''
        # ensure we have an AppConfig object (recurse to all DMP apps if None)
        if isinstance(app, str):
            app = apps.get_app_config(app)

        # add to the set of DMP-enabled apps
        self.dmp_enabled_apps.add(app.name)

        # set up the template, script, and style renderers
        # these create and cache just by accessing them
        self.get_template_loader(app, 'templates', create=True)
        self.get_template_loader(app, 'scripts', create=True)
        self.get_template_loader(app, 'styles', create=True)

        # add the shortcut functions (only to the main templates, we don't do to scripts or styles
        # because people generally don't call those directly).  This is a monkey patch, but it is
        # an incredibly useful one because it makes calling app-specific rendering functions much
        # easier.
        #
        # Django's shortcut to return an *HttpResponse* is render(), and its template method to render a *string* is also render().
        # Good job on naming there, folks.  That's going to confuse everyone.  But I'm matching it to be consistent despite the potential confusion.
        with self.rlock:
            app.module.dmp_render_to_string = _render_to_string(self, app.name)
            app.module.dmp_render = _render(self, app.name)


    def is_dmp_app(self, app):
        '''
        Returns True if the given app is a DMP-enabled app.  The app parameter can
        be either the name of the app or an AppConfig object.
        '''
        if isinstance(app, AppConfig):
            app = app.name
        return app in self.dmp_enabled_apps


    def from_string(self, template_code):
        '''
        Compiles a template from the given string.
        This is one of the required methods of Django template engines.
        '''
        mako_template = Template(template_code, imports=DMP_OPTIONS.get('DEFAULT_TEMPLATE_IMPORTS'), input_encoding=DMP_OPTIONS.get('DEFAULT_TEMPLATE_ENCODING', 'utf-8'))
        return MakoTemplateAdapter(mako_template)


    def get_view_function(self, app_name, module_name, function_name, fallback_template_name):
        '''
        Returns the view function for the given app_name + module_name + function_name.
        If not found, it returns the view function for the fallback_template_name within app_name.
        If still not found, raises a ViewDoesNotExist exception.

        This method uses a cache for a significant speedup.  The cache use is thread safe.
        It primarily used by the DMP router.
        '''
        # get the function (or error) from the cache
        cache_key = ( app_name, module_name, function_name )
        try:
            return self.view_cache[cache_key]
        except KeyError:
            # acquire the lock and try the cache again (another thread might have put it in cache while we are waiting for lock)
            with self.rlock:
                try:
                    return self.view_cache[cache_key]
                except KeyError:  # really not in the cache, so let's go get it
                    # check if the module exists. i'm using find_spec instead of import_module
                    # to know if it exists because import_module fails on things like syntax error,
                    # and the programmer should see these.
                    func_obj = None
                    if find_spec(module_name) is not None:
                        module_obj = import_module(module_name)
                        func_obj = getattr(module_obj, function_name, None)
                        if func_obj == None:
                            func_obj = DMPViewDoesNotExist('Module {} found successfully, but view function {} is not defined in the module.'.format(module_name, function_name))

                    # check for not found, no @view_function, View subclass
                    if func_obj == None:
                        # try to load the template directly
                        try:
                            func_obj = TemplateViewFunction(app_name, fallback_template_name)
                            func_obj.get_template()  # check whether the template exists
                        except TemplateDoesNotExist as e:
                            func_obj = DMPViewDoesNotExist('View function {}.{} not found, and fallback template {} not found.'.format(module_name, function_name, fallback_template_name))

                    elif isclass(func_obj) and issubclass(func_obj, View):
                        # this Django method wraps the view class with a function, so now we can treat it like a regular dmp view function
                        func_obj = func_obj.as_view()
                        func_obj._dmp_view_type = DMP_VIEW_CLASS_METHOD  # have to monkey patch in this case because we don't control the as_view() method of View

                    # the function must be DMP_VIEW_* (see util.py)
                    if getattr(func_obj, '_dmp_view_type', None) == None:
                        func_obj = DMPViewDoesNotExist('View function {}.{} found successfully, but it must be decorated with @view_function.  Note that if you have multiple decorators on a function, the @view_function decorator must be listed first.'.format(module_name, function_name))

                    # cache the result (if production)
                    if not settings.DEBUG:
                        self.view_cache[cache_key] = func_obj

                    # return the obj!
                    return func_obj

        # the code should never be able to get here
        raise Exception("Django-Mako-Plus error: The get_view_function() function should not have been able to get to this point.  Please notify the owner of the DMP project.  Thanks.")


    def get_template(self, template_name):
        '''
        Retrieves a template object.
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
        loader = MakoTemplateLoader(path, None)

        # cache if we are allowed
        if use_cache:
            self.template_loaders[path] = loader

        # return
        return loader



############################################################################
###  Monkey-patch functions to enable render() and render_to_string()
###  within the app scope of *each* DMP-enabled app.


def _render_to_string(dmp_instance, app_name):
    # I'm doing this inner function for late lookups (get_template_loader), just in case new template loader objects are added after creation.
    def wrapper(request, template, context=None, def_name=None, subdir='templates'):
        '''
        A shortcut to render a template.  This is one of the primary functions in the DMP framework.
        This method is added to the app space of each DMP-enabled app at load time.

            @request      The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                          file will be ignored but the template will otherwise render fine.
            @template     The template file path to render.  This is relative to the app_path/controller_TEMPLATES_DIR/ directory.
                          For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                          set up the variables as described in the documentation above.
            @context      A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                          or a Django Context object.
            @def_name     Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                          For example, def_name="foo" will call <%block name="foo"></%block> or <%def name="foo()"></def> within the template.
            @subdir       The sub-folder within the app where the template resides.  Templates are normally placed
                          in project/appname/templates/, which is the default value.

        Returns the rendered template as a unicode string.

        Examples of use from within appname/views/someview.py:

            from django_mako_plus import view_function
            from .. import render

            @view_function
            def process_request(request):
                # render an HTML template in appname/templates/sometemplate.html to a string
                html = render_to_string(request, 'sometemplate.html', { 'var1': 'value' })
                # (do something with the html)

            @view_function
            def another_func(request):
                # render some dynamic JS in appname/scripts/sometemplate.js (which has embedded Mako code)
                html = render_to_string(request, 'sometemplate.js', { 'var1': 'value' }, subdir="scripts")
                # (do something with the html)

            @view_function
            def yet_another(request):
                # render a single <block name="toolbar"> instead of the entire template in appname/templates/sometemplate.html to a string
                html = render_to_string(request, 'sometemplate.html', { 'var1': 'value' }, def_name='toolbar')
                # (do something with the html)

        The method triggers two signals:
            1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
               the normal template object that is used for the render operation.
            2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
               template object render.
        '''
        template_loader = dmp_instance.get_template_loader(app_name, subdir)
        template_adapter = template_loader.get_template(template)
        return getattr(template_adapter, 'render')(context=context, request=request, def_name=def_name)

    # outer function return
    return wrapper


def _render(dmp_instance, app_name):
    # I'm doing this inner function for late lookups (get_template_loader), just in case new template loader objects are added after creation.
    def wrapper(request, template, context=None, def_name=None, subdir='templates', content_type=None, status=None, charset=None):
        '''
        A shortcut to render a template.  This is one of the primary functions in the DMP framework.
        This method is added to the app space of each DMP-enabled app at load time.

            @request      The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                          file will be ignored but the template will otherwise render fine.
            @template     The template file path to render.  This is relative to the app_path/controller_TEMPLATES_DIR/ directory.
                          For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                          set up the variables as described in the documentation above.
            @context      A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                          or a Django Context object.
            @def_name     Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                          For example, def_name="foo" will call <%block name="foo"></%block> or <%def name="foo()"></def> within the template.
            @subdir       The sub-folder within the app where the template resides.  Templates are normally placed
                          in project/appname/templates/, which is the default value.
            @content_type The MIME type of the response.  Defaults to settings.DEFAULT_CONTENT_TYPE (usually 'text/html').
            @status       The HTTP response status code.  Defaults to 200 (OK).
            @charset      The charset to encode the processed template string (the output) with.  Defaults to settings.DEFAULT_CHARSET (usually 'utf-8').

        Returns a Django HttpResponse containing the rendered template.

        Examples of use from within appname/views/someview.py:

            from django_mako_plus import view_function
            from .. import render

            @view_function
            def process_request(request):
                # return an HTML template in appname/templates/sometemplate.html
                return render_to_string(request, 'sometemplate.html', { 'var1': 'value' })

            @view_function
            def another_func(request):
                # return some dynamic JS in appname/scripts/sometemplate.js (which has embedded Mako code)
                return render_to_string(request, 'sometemplate.js', { 'var1': 'value' }, subdir="scripts")

            @view_function
            def yet_another(request):
                # return a single <block name="toolbar"> instead of the entire template in appname/templates/sometemplate.html
                return render_to_string(request, 'sometemplate.html', { 'var1': 'value' }, def_name='toolbar')

        The method triggers two signals:
            1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
               the normal template object that is used for the render operation.
            2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
               template object render.
        '''
        template_loader = dmp_instance.get_template_loader(app_name, subdir)
        template_adapter = template_loader.get_template(template)
        return getattr(template_adapter, 'render_to_response')(context=context, request=request, def_name=def_name, content_type=content_type, status=status, charset=charset)

    # outer function return
    return wrapper

