from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ViewDoesNotExist
from django.http import Http404, HttpResponse, HttpResponseServerError, StreamingHttpResponse
from django.http import Http404, HttpResponseNotAllowed
from django.template import TemplateDoesNotExist
from django.views.generic import View

from .converter import ConversionTask
from .decorators import view_function, NotDecoratedError
from .exceptions import BaseRedirectException, InternalRedirectException, RedirectException
from .signals import dmp_signal_pre_process_request, dmp_signal_post_process_request, dmp_signal_internal_redirect_exception, dmp_signal_redirect_exception
from .util import DMP_OPTIONS, get_dmp_instance, log

import inspect
import sys
import threading
from importlib import import_module
from importlib.util import find_spec


# lock to keep get_router() thread safe
rlock = threading.RLock()

# the cache of mini-routers
CACHED_ROUTERS = {}


##############################################################
###   The front controller of all views on the site.
###   urls.py routes everything through this method.

def route_request(request, *args, **kwargs):
    '''
    The main router for all calls coming in to the system.  Patterns in urls.py should call this function.
    '''
    # check to ensure DMP's middleware ran
    # wrap to enable the InternalRedirectExceptions to loop around
    response = None
    while True:
        # an outer try that catches the redirect exceptions
        try:
            # ensure the middleware ran
            if getattr(request, 'dmp', None) is None:
                raise ImproperlyConfigured("Variable request.dmp.function_obj does not exist (check MIDDLEWARE for `django_mako_plus.RequestInitMiddleware`).")

            # output the variables so the programmer can debug where this is routing
            log.info(str(request.dmp))

            # if we had a view not found, raise a 404
            if isinstance(request.dmp.function_obj, RegistryExceptionRouter):
                log.info(request.dmp.function_obj.message(request))
                return request.dmp.function_obj.get_response(request, *args, **kwargs)

            # log the view
            log.info('calling %s', request.dmp.function_obj.message(request))

            # call view function with any args and any remaining kwargs
            response = request.dmp.function_obj.get_response(request, *args, **kwargs)

            # if we didn't get a correct response back, send a 500
            if not isinstance(response, (HttpResponse, StreamingHttpResponse)):
                msg = '%s failed to return an HttpResponse (or the post-signal overwrote it).  Returning 500 error.' % request.dmp.function_obj.message(request)
                log.info(msg)
                return HttpResponseServerError(msg)

            # return the response
            return response

        except InternalRedirectException as ivr:
            # send the signal
            if DMP_OPTIONS['SIGNALS']:
                dmp_signal_internal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=ivr)
            # resolve to a function
            request.dmp.module = ivr.redirect_module
            request.dmp.function = ivr.redirect_function
            log.info('received an InternalViewRedirect to %s.%s', request.dmp.module, request.dmp.function)
            request.dmp.function_obj = get_router(request.dmp.module, request.dmp.function, verify_decorator=False)
            if isinstance(request.dmp.function_obj, RegistryExceptionRouter):
                log.info('could not fulfill InternalViewRedirect because %s.%s does not exist.', request.dmp.module, request.dmp.function)
            # let it wrap back to the top of the "while True" loop to restart the routing

        except RedirectException as e: # redirect to another page
            if request.dmp.class_obj is None:
                log.info('%s redirected processing to %s', request.dmp.function_obj.message(request), e.redirect_to)
            # send the signal
            if DMP_OPTIONS['SIGNALS']:
                dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
            # send the browser the redirect command
            return e.get_response(request)

    # the code should never get here
    raise Exception("Django-Mako-Plus error: The route_request() function should not have been able to get to this point.  Please notify the owner of the DMP project.  Thanks.")



########################################################
###   Cache of mini routers

def get_router(module_name, function_name, fallback_app=None, fallback_template=None, verify_decorator=True):
    '''
    Gets or creates a mini-router for module_name.function_name.
    Returns one of the four mini-routers defined later in this file.
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

        # get the converter from the decorator kwargs, if there is one
        try:
            decorator_kwargs = view_function.get_kwargs(func)[0]
        except NotDecoratedError:
            decorator_kwargs = {}

        # class-based view?
        if inspect.isclass(func) and issubclass(func, View):
            return ClassBasedRouter(module, func(), decorator_kwargs)  # func() to instantiate because func is class (not instance)

        # a view function?
        if verify_decorator and not view_function.is_decorated(func):
            raise ViewDoesNotExist("View {}.{} was found successfully, but it must be decorated with @view_function or be a subclass of django.views.generic.View.".format(module_name, function_name))
        return ViewFunctionRouter(module, func, decorator_kwargs)

    except ViewDoesNotExist as vdne:
        return RegistryExceptionRouter(vdne)




########################################################################################
###   Router classes for single endpoints.  When a view is first accessed, one
###   of these "mini" routers is created for it and cached for future calls.


class ViewFunctionRouter(object):
    '''Router for view functions and class-based methods'''
    def __init__(self, mod, func, decorator_kwargs):
        self.module = mod
        self.function = func
        self.decorator_kwargs = decorator_kwargs
        self.signature = inspect.signature(func)
        # map the type hints
        param_types = getattr(func, '__annotations__', {})  # not using typing.get_type_hints because it adds Optional() to None defaults, and we don't need to follow mro here
        # inspect the parameters of the view function
        params = []
        for i, p in enumerate(self.signature.parameters.values()):
            params.append(ViewParameter(
                name=p.name,
                position=i,
                kind=p.kind,
                type=param_types.get(p.name) or inspect.Parameter.empty,
                default=p.default,
            ))
        self.parameters = tuple(params)


    def get_response(self, *args, **kwargs):
        '''Converts urlparams, calls the view function, returns the response'''
        # leaving request inside *args (or kwargs) so we can convert it like anything else (and parameter indices aren't off by one)
        request = kwargs.get('request', args[0])
        ctask = ConversionTask(request, self.module, self.function, self.decorator_kwargs)
        args = list(args)
        urlparam_i = 0
        # add urlparams into the arguments and convert the values
        for parameter_i, parameter in enumerate(self.parameters):
            try:
                # skip *args, **kwargs
                if parameter.kind is inspect.Parameter.VAR_POSITIONAL or parameter.kind is inspect.Parameter.VAR_KEYWORD:
                    continue
                # value in kwargs?
                elif parameter.name in kwargs:
                    kwargs[parameter.name] = ctask.converter(kwargs[parameter.name], parameter, ctask)
                # value in args?
                elif parameter_i < len(args):
                    args[parameter_i] = ctask.converter(args[parameter_i], parameter, ctask)
                # urlparam value?
                elif urlparam_i < len(request.dmp.urlparams):
                    kwargs[parameter.name] = ctask.converter(request.dmp.urlparams[urlparam_i], parameter, ctask)
                    urlparam_i += 1
                # can we assign a default value?
                elif parameter.default is not inspect.Parameter.empty:
                    kwargs[parameter.name] = ctask.converter(parameter.default, parameter, ctask)
                # fallback is None
                else:
                    kwargs[parameter.name] = ctask.converter(None, parameter, ctask)

            except BaseRedirectException as e:
                log.info('Redirect exception raised during conversion of parameter %s (%s): %s', parameter.position, parameter.name, e)
                raise
            except Http404 as e:
                log.info('Raising Http404 because exception raised during conversion of parameter %s (%s): %s', parameter.position, parameter.name, e, exc_info=e)
                raise
            except Exception as e:
                log.info('Raising Http404 because exception raised during conversion of parameter %s (%s): %s', parameter.position, parameter.name, e, exc_info=e)
                raise Http404('Invalid parameter specified in the url')

        # send the pre-signal
        if DMP_OPTIONS['SIGNALS']:
            for receiver, ret_response in dmp_signal_pre_process_request.send(sender=sys.modules[__name__], request=request, view_args=args, view_kwargs=kwargs):
                if isinstance(ret_response, (HttpResponse, StreamingHttpResponse)):
                    return ret_response

        # call the view!
        response = self.function(*args, **kwargs)

        # send the post-signal
        if DMP_OPTIONS['SIGNALS']:
            for receiver, ret_response in dmp_signal_post_process_request.send(sender=sys.modules[__name__], request=request, response=response, view_args=args, view_kwargs=kwargs):
                if ret_response is not None:
                    response = ret_response # sets it to the last non-None in the signal receiver chain

        # return the response
        return response


    def message(self, request):
        return 'view function {}.{}'.format(request.dmp.module, request.dmp.function)



class ClassBasedRouter(object):
    '''Router for class-based views.'''
    def __init__(self, module, instance, decorator_kwargs):
        self.instance = instance
        self.endpoints = {}
        for mthd_name in instance.http_method_names:  # get parameters from the first http-based method (get, post, etc.)
            func = getattr(instance, mthd_name, None)
            if func is not None:
                self.endpoints[mthd_name] = ViewFunctionRouter(module, func, decorator_kwargs)


    def get_response(self, request, *args, **kwargs):
        endpoint = self.endpoints.get(request.method.lower())
        if endpoint is not None:
            return endpoint.get_response(request, **kwargs)
        log.info('Method Not Allowed (%s): %s', request.method, request.path, extra={'status_code': 405, 'request': request})
        return HttpResponseNotAllowed([ e.upper() for e in self.endpoints.keys() ])


    @property
    def name(self):
        return self.instance.__class__.__qualname__


    def message(self, request):
        return 'class-based view function {}.{}.{}'.format(request.dmp.module, self.name, request.dmp.function)



class TemplateViewRouter(object):
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


    def message(self, request):
        return 'template {} (view function {}.{} not found)'.format(self.template_name, request.dmp.module, request.dmp.function)



class RegistryExceptionRouter(object):
    '''Router for a registry exception (i.e. view not found).'''
    def __init__(self, exc):
        self.exc = exc


    def get_response(self, request, *args, **kwargs):
        raise Http404(str(self.exc))


    def message(self, request):
        return str(self.exc)



#####################################
###  ViewParameter

class ViewParameter(object):
    '''
    A data class that represents a view parameter on a view function.
    An instance of this class is created for each parameter in a view function
    (except the initial request object argument).
    '''
    def __init__(self, name, position, kind, type, default):
        '''
        name:      The name of the parameter.
        position:  The position of this parameter.
        kind:      The kind of argument (positional, keyword, etc.). See inspect module.
        type:      The expected type of this parameter.  Converters use this type to
                   convert urlparam strings to the right type.
        default:   Any default value, specified in function type hints.  If no default is
                   specified in the function, this is `inspect.Parameter.empty`.
        '''
        self.name = name
        self.position = position
        self.kind = kind
        self.type = type
        self.default = default

    def __str__(self):
        return 'ViewParameter: name={}, type={}, default={}'.format(
            self.name,
            self.type.__qualname__ if self.type is not None else '<not specified>',
            self.default,
        )



