
from ..decorators import BaseDecorator
from ..registry import ensure_dmp_app
from ..util import URLParamList, get_dmp_instance
from .discover import get_view_function

from urllib.parse import unquote


class RoutingData(object):
    '''
    The routing information for a request.  This is basically an enhanced ResolverMatch,
    but since Django creates its own ResolverMatch object during resolution (throwing ours
    away), this is stored in a per-request decorator on the actual view function.

    During view middleware, this object is also attached to the request as `request.dmp`.
    '''
    def __init__(self, app=None, page=None, function=None, urlparams=None):
        '''These variables are set by the process_view method above'''
        # the request object is set later by the middleware so the render methods work
        self.request = None

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
            self.callable = get_view_function(self.module, self.function, self.app, fallback_template)
        else:
            self.module = None
            self.callable = None
        self.view_type = self.callable.view_type if self.callable is not None else None

        # parse the urlparams
        # note that I'm not using unquote_plus because the + switches to a space *after* the question mark (in the regular parameters)
        # in the normal url, spaces should be quoted with %20.  Thanks Rosie for the tip.
        if isinstance(urlparams, (list, tuple)):
            self.urlparams = URLParamList(urlparams)
        elif urlparams:
            self.urlparams = URLParamList(( unquote(s) for s in urlparams.split('/') ))
        else:
            self.urlparams = URLParamList()


    def __repr__(self):
        return '<RoutingData app={}, page={}, module={}, function={}, view_type={}, urlparams={}>'.format(
             self.app,
             self.page,
             self.module,
             self.function,
             self.view_type,
             self.urlparams,
        )


    def _debug(self):
        return 'django_mako_plus RoutingData:' + \
            ''.join(('\n\t{: <16}{}'.format(k, v) for k, v in (
                ( 'app', self.app ),
                ( 'page', self.page ),
                ( 'module', self.module ),
                ( 'function', self.function ),
                ( 'callable', self.callable ),
                ( 'view_type', self.view_type ),
                ( 'urlparams', self.urlparams ),
            )))


    def render(self, template, context=None, def_name=None, subdir='templates', content_type=None, status=None, charset=None):
        '''App-specific render function that renders templates in the *current app*, attached to the request for convenience'''
        if self.request is None:
            raise ValueError("RoutingData.render() can only be called after the view middleware is run.")
        ensure_dmp_app(self.app)
        template_loader = get_dmp_instance().get_template_loader(self.app, subdir)
        template_adapter = template_loader.get_template(template)
        return getattr(template_adapter, 'render_to_response')(context=context, request=self.request, def_name=def_name, content_type=content_type, status=status, charset=charset)


    def render_to_string(self, template, context=None, def_name=None, subdir='templates'):
        '''App-specific render function that renders templates in the *current app*, attached to the request for convenience'''
        if self.request is None:
            raise ValueError("RoutingData.render() can only be called after the view middleware is run.")
        ensure_dmp_app(self.app)
        template_loader = get_dmp_instance().get_template_loader(self.app, subdir)
        template_adapter = template_loader.get_template(template)
        return getattr(template_adapter, 'render')(context=context, request=self.request, def_name=def_name)