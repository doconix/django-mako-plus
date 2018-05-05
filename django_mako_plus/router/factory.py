from django.conf import settings
from django.core.exceptions import ViewDoesNotExist
from django.template import TemplateDoesNotExist
from django.views.generic import View

from .router_class import ClassBasedRouter
from .router_exception import RegistryExceptionRouter
from .router_function import ViewFunctionRouter
from .router_template import TemplateViewRouter

from .decorators import view_function

import inspect
import threading
from importlib import import_module
from importlib.util import find_spec




########################################################
###   Cached routers

CACHED_ROUTERS = {}
rlock = threading.RLock()

def get_router(module_name, function_name, fallback_app=None, fallback_template=None, verify_decorator=True):
    '''
    Gets or creates a mini-router for module_name.function_name.
    If the module or function cannot be found, ViewDoesNotExist is raised.
    '''
    # first check the cache
    key = ( module_name, function_name )
    try:
        return CACHED_ROUTERS[key]
    except KeyError:
        with rlock:
            # try again now that we're locked
            try:
                return CACHED_ROUTERS[key]
            except KeyError:
                func = router_factory(module_name, function_name, fallback_app, fallback_template, verify_decorator)
                if not settings.DEBUG:  # only cache in production mode
                    CACHED_ROUTERS[key] = func
                return func

    # the code should never be able to get here
    raise Exception("Django-Mako-Plus error: registry.get_router() should not have been able to get to this point.  Please notify the owner of the DMP project.  Thanks.")



############################################################
###   Creates the appropriate router for a
###   view function, class-based view function,
###   template, or error.

def router_factory(module_name, function_name, fallback_app=None, fallback_template=None, verify_decorator=True):
    '''
    Factory method to create a view-specific router in the system.
    See the four mini-routers at the end of this file.
    '''
    try:
        # I'm first calling find_spec first here beacuse I don't want import_module in
        # a try/except -- there are lots of reasons that importing can fail, and I just want to
        # know whether the file actually exists.  find_spec raises AttributeError if not found.
        try:
            spec = find_spec(module_name)
        except ValueError:
            spec = None
        if spec is None:
            # no view module, can we call the template directly?
            try:
                return TemplateViewRouter(fallback_app, fallback_template)
            except TemplateDoesNotExist as e:
                raise ViewDoesNotExist('View module {} not found, and fallback template {} could not be loaded ({})'.format(module_name, fallback_template, e))

        # load the module and function
        try:
            module = import_module(module_name)
            func = getattr(module, function_name)
        except ImportError as e:
            raise ViewDoesNotExist('Module "{}" could not be imported: {}'.format(module_name, e))
        except AttributeError as e:
            raise ViewDoesNotExist('Module "{}" found successfully, but "{}" was not found: {}'.format(module_name, function_name, e))

        # class-based view?
        if inspect.isclass(func) and issubclass(func, View):
            # must do func() to instantiate because func is class (not a function)
            return ClassBasedRouter(module, func())

        # a view function?
        if verify_decorator and not view_function._is_decorated(func):
            raise ViewDoesNotExist("View {}.{} was found successfully, but it must be decorated with @view_function or be a subclass of django.views.generic.View.".format(module_name, function_name))
        return ViewFunctionRouter(module, func)

    except ViewDoesNotExist as vdne:
        return RegistryExceptionRouter(vdne)
