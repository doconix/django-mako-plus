from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseServerError, StreamingHttpResponse

from .factory import get_router
from .router_class import ClassBasedRouter
from .router_exception import RegistryExceptionRouter

from ..exceptions import InternalRedirectException, RedirectException
from ..registry import ensure_dmp_app
from ..signals import dmp_signal_internal_redirect_exception, dmp_signal_redirect_exception
from ..util import DMP_OPTIONS, get_dmp_instance, log, URLParamList

import sys

from urllib.parse import unquote




##############################################################
###   The front controller of all views on the site.
###   urls.py routes everything through this method.

def route_request(request, *args, **kwargs):
    '''
    The main router for all calls coming in to the system.  Patterns in urls.py should call this function.
    '''
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
        # update the RoutingData object
        request.dmp.module = ivr.redirect_module
        request.dmp.function = ivr.redirect_function
        request.dmp._set_function_obj(request, get_router(request.dmp.module, request.dmp.function, verify_decorator=False))
        if isinstance(request.dmp.function_obj, RegistryExceptionRouter):
            log.info('could not fulfill InternalViewRedirect because %s.%s does not exist.', request.dmp.module, request.dmp.function)
        # recurse with the same info
        log.info('received an InternalViewRedirect to %s.%s', request.dmp.module, request.dmp.function)
        return route_request(request, *args, **kwargs)

    except RedirectException as e: # redirect to another page
        if request.dmp.class_obj is None:
            log.info('%s redirected processing to %s', request.dmp.function_obj.message(request), e.redirect_to)
        # send the signal
        if DMP_OPTIONS['SIGNALS']:
            dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
        # send the browser the redirect command
        return e.get_response(request)

    # the code should never get here




#########################################################
###  Routing data for DMP.  Attached as `request.dmp`
###  by the middleware.


class RoutingData(object):
    '''
    A default object is set at the beginning of the request.
    Then after the url pattern is matched, an object with the
    match data is created.
    '''
    def __init__(self, request=None, app=None, page=None, function=None, urlparams=None):
        '''These variables are set by the process_view method above'''
        self.request = request

        # period and dash cannot be in python names, but we allow dash in app, dash in page, and dash/period in function
        self.app = app.replace('-', '_') if app is not None else None
        self.page = page.replace('-', '_') if page is not None else None
        if function:
            self.function = function.replace('.', '_').replace('-', '_')
            fallback_template = '{}.{}.html'.format(page, function)
        else:
            self.function = 'process_request'
            fallback_template = '{}.html'.format(page)

        # set the module and function
        # the return of get_router_function might be a function, a class-based view, or a template
        if self.app is not None and self.page is not None:
            self.module = '.'.join([ self.app, 'views', self.page ])
            self._set_function_obj(self.request, get_router(self.module, self.function, self.app, fallback_template))
        else:
            self.module = None
            self.class_obj = None
            self.function_obj = None

        # parse the urlparams
        # note that I'm not using unquote_plus because the + switches to a space *after* the question mark (in the regular parameters)
        # in the normal url, spaces should be quoted with %20.  Thanks Rosie for the tip.
        if isinstance(urlparams, (list, tuple)):
            self.urlparams = URLParamList(urlparams)
        elif urlparams:
            self.urlparams = URLParamList(( unquote(s) for s in urlparams.split('/') ))
        else:
            self.urlparams = URLParamList()


    def _set_function_obj(self, request, function_obj):
        '''Sets the function object, with alterations if class-based routing'''
        self.class_obj = None
        self.function_obj = function_obj
        if isinstance(self.function_obj, ClassBasedRouter):
            self.class_obj = self.function_obj
            self.function = request.method.lower()


    def __repr__(self):
        return 'RoutingData: app={}, page={}, module={}, function={}, urlparams={}'.format(
             self.app,
             self.page,
             self.module if self.class_obj is None else (self.module + '.' + self.class_obj.name),
             self.function,
             self.urlparams,
        )

    def _debug(self):
        return 'django_mako_plus RoutingData:' + \
            ''.join(('\n\t{: <16}{}'.format(k, v) for k, v in (
                ( 'app', self.app ),
                ( 'page', self.page ),
                ( 'module', self.module ),
                ( 'function', self.function ),
                ( 'class_obj', self.class_obj ),
                ( 'function_obj', self.function_obj ),
                ( 'urlparams', self.urlparams ),
            )))


    def render(self, template, context=None, def_name=None, subdir='templates', content_type=None, status=None, charset=None):
        '''App-specific render function that renders templates in the *current app*, attached to the request for convenience'''
        ensure_dmp_app(self.app)
        template_loader = get_dmp_instance().get_template_loader(self.app, subdir)
        template_adapter = template_loader.get_template(template)
        return getattr(template_adapter, 'render_to_response')(context=context, request=self.request, def_name=def_name, content_type=content_type, status=status, charset=charset)


    def render_to_string(self, template, context=None, def_name=None, subdir='templates'):
        '''App-specific render function that renders templates in the *current app*, attached to the request for convenience'''
        ensure_dmp_app(self.app)
        template_loader = get_dmp_instance().get_template_loader(self.app, subdir)
        template_adapter = template_loader.get_template(template)
        return getattr(template_adapter, 'render')(context=context, request=self.request, def_name=def_name)
