
from .factory import get_router
from .router_class import ClassBasedRouter

from ..registry import ensure_dmp_app
from ..util import URLParamList, get_dmp_instance


from urllib.parse import unquote


class RoutingData(object):
    '''
    A default object is set at the beginning of the request.
    Then after the url pattern is matched, an object with the
    match data is created.

    This is attached to the request as `request.dmp`.
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
