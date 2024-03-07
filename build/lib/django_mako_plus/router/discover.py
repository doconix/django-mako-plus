from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ViewDoesNotExist
from django.template import TemplateDoesNotExist
from django.views.generic import View

from .decorators import view_function, CONVERTER_ATTRIBUTE_NAME
from ..util import import_qualified, log

import inspect
import threading
from importlib import import_module
from importlib.util import find_spec



########################################################
###   Cached routers

CACHED_VIEW_FUNCTIONS = {}
rlock = threading.RLock()


def get_view_function(module_name, function_name, fallback_app=None, fallback_template=None, verify_decorator=True):
    '''
    Retrieves a view function from the cache, finding it if the first time.
    Raises ViewDoesNotExist if not found.  This is called by resolver.py.
    '''
    # first check the cache (without doing locks)
    key = ( module_name, function_name )
    try:
        return CACHED_VIEW_FUNCTIONS[key]
    except KeyError:
        with rlock:
            # try again now that we're locked
            try:
                return CACHED_VIEW_FUNCTIONS[key]
            except KeyError:
                # if we get here, we need to load the view function
                func = find_view_function(module_name, function_name, fallback_app, fallback_template, verify_decorator)
                # cache in production mode
                if not settings.DEBUG:
                    CACHED_VIEW_FUNCTIONS[key] = func
                return func

    # the code should never be able to get here
    raise Exception("Django-Mako-Plus error: get_view_function() should not have been able to get to this point.  Please notify the owner of the DMP project.  Thanks.")


def find_view_function(module_name, function_name, fallback_app=None, fallback_template=None, verify_decorator=True):
    '''
    Finds a view function, class-based view, or template view.
    Raises ViewDoesNotExist if not found.
    '''
    dmp = apps.get_app_config('django_mako_plus')

    # I'm first calling find_spec first here beacuse I don't want import_module in
    # a try/except -- there are lots of reasons that importing can fail, and I just want to
    # know whether the file actually exists.  find_spec raises AttributeError if not found.
    try:
        spec = find_spec(module_name)
    except ValueError:
        spec = None
    if spec is None:
        # no view module, so create a view function that directly renders the template
        try:
            return create_view_for_template(fallback_app, fallback_template)
        except TemplateDoesNotExist as e:
            raise ViewDoesNotExist('view module {} not found, and fallback template {} could not be loaded ({})'.format(module_name, fallback_template, e))

    # load the module and function
    try:
        module = import_module(module_name)
        func = getattr(module, function_name)
        func.view_type = 'function'
    except ImportError as e:
        raise ViewDoesNotExist('module "{}" could not be imported: {}'.format(module_name, e))
    except AttributeError as e:
        raise ViewDoesNotExist('module "{}" found successfully, but "{}" was not found: {}'.format(module_name, function_name, e))

    # if class-based view, call as_view() to get a view function to it
    if inspect.isclass(func) and issubclass(func, View):
        func = func.as_view()
        func.view_type = 'class'

    # if regular view function, check the decorator
    elif verify_decorator and not view_function.is_decorated(func):
        raise ViewDoesNotExist("view {}.{} was found successfully, but it must be decorated with @view_function or be a subclass of django.views.generic.View.".format(module_name, function_name))

    # attach a converter to the view function
    if dmp.options['PARAMETER_CONVERTER'] is not None:
        try:
            converter = import_qualified(dmp.options['PARAMETER_CONVERTER'])(func)
            setattr(func, CONVERTER_ATTRIBUTE_NAME, converter)
        except ImportError as e:
            raise ImproperlyConfigured('Cannot find PARAMETER_CONVERTER: {}'.format(str(e)))

    # return the function/class
    return func


def create_view_for_template(app_name, template_name):
    '''
    Creates a view function for templates (used whe a view.py file doesn't exist but the .html does)
    Raises TemplateDoesNotExist if the template doesn't exist.
    '''
    # ensure the template exists
    apps.get_app_config('django_mako_plus').engine.get_template_loader(app_name).get_template(template_name)
    # create the view function
    def template_view(request, *args, **kwargs):
        # not caching the template object (getting it each time) because Mako has its own cache
        dmp = apps.get_app_config('django_mako_plus')
        template = dmp.engine.get_template_loader(app_name).get_template(template_name)
        return template.render_to_response(request=request, context=kwargs)
    template_view.view_type = 'template'
    return template_view
