from urllib.parse import unquote

# try to import MiddlewareMixIn (Django 1.10+)
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # create a dummy MiddlewareMixin if older Django
    MiddlewareMixin = object

from .registry import ensure_dmp_app
from .router import ClassBasedRouter, get_router
from .util import DMP_OPTIONS, URLParamList, get_dmp_instance


##########################################################
###   Middleware the prepares the request for
###   use with the controller.


class RequestInitMiddleware(MiddlewareMixin):
    '''
    Adds several fields to the request that our controller needs.
    Projects can customize the variables with view middleware that runs after this class.

    This class must be included in settings.py -> MIDDLEWARE.
    '''
    def process_request(self, request):
        '''
        Adds stubs for the DMP custom variables to the request object.

        We do this early in the middleware process because process_view() below gets called
        *after* URL resolution.  If an exception occurs before that (a 404, a middleware exception),
        the variables won't be put on the request object.  Therefore, we put stubs on it at the
        earliest possible place so they exist even if we don't get to process_view().
        '''
        request.dmp = INITIAL_ROUTING_DATA


    def process_view(self, request, view_func, view_args, view_kwargs):
        '''
        Adds the following to the request object:

            request.dmp.app            The Django application (such as "homepage"), as a string.
            request.dmp.page           The view module (such as "index" for index.py), as a string.
            request.dmp.function       The function within the view module to be called (usually "process_request"),
                                       as a string.
            request.dmp.module         The module path in Python terms (such as homepage.views.index), as a string.
            request.dmp.class_obj      The class object, if a class-based view.
            request.dmp.function_obj   The view callable (function, method, etc.) to be called by the router.
            request.dmp.urlparams      A list of the remaining url parts, as a list of strings.
                                       View function parameter conversion uses the values in this list.

        As view middleware, this function runs just before the router.route_request is called.
        '''
        # ensure this hasn't run twice (such as having it in the middleware twice)
        if request.dmp is not INITIAL_ROUTING_DATA:
            return

        # create the RoutingData object
        request.dmp = RoutingData(
            request,
            view_kwargs.pop('dmp_app', None) or DMP_OPTIONS['DEFAULT_APP'],
            view_kwargs.pop('dmp_page', None) or DMP_OPTIONS['DEFAULT_PAGE'],
            view_kwargs.pop('dmp_function', None),
            view_kwargs.pop('dmp_urlparams', '').strip(),
        )


class RoutingData(object):
    '''
    The routing data for DMP.

    An default object is set at the beginning of the request.
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
            self.class_obj = None
            self.function_obj = get_router(self.module, self.function, self.app, fallback_template)
            if isinstance(self.function_obj, ClassBasedRouter):
                self.class_obj = self.function_obj
                self.function = request.method.lower()
        else:
            self.module = None
            self.class_obj = None
            self.function_obj = None

        # parse the urlparams
        # note that I'm not using unquote_plus because the + switches to a space *after* the question mark (in the regular parameters)
        # in the normal url, spaces should be quoted with %20.  Thanks Rosie for the tip.
        self.urlparams = URLParamList(( unquote(s) for s in urlparams.split('/') )) if urlparams else URLParamList()


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
        return getattr(template_adapter, 'render')(context=context, request=request, def_name=def_name)




# This singleton is set on the request object early in the request (during middleware).
# Once urls.py has processed, request.dmp is changed to a populated RoutingData object.
INITIAL_ROUTING_DATA = RoutingData()
