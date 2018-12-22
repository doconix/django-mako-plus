from django.apps import apps

from ..decorators import BaseDecorator
from ..util import URLParamList
from .discover import get_view_function

from urllib.parse import unquote


class RoutingData(object):
    '''
    The routing information for a request.  This is created during url resolution when a pattern
    matches (see resolver.py).

    During middleware, this is not available
        request.dmp.app         The Django application (such as "homepage"), as a string.
        request.dmp.page        The view module (such as "index" for index.py), as a string.
        request.dmp.function    The function within the view module to be called (usually "process_request"),
                                as a string.
        request.dmp.module      The module path in Python terms (such as homepage.views.index), as a string.
        request.dmp.callable    The view callable (function, method, etc.) to be called by the router.
        request.dmp.view_type   The type of view: function, class, or template.
        request.dmp.urlparams   A list of the remaining url parts, as a list of strings. Parameter conversion
                                uses the values in this list.

    '''
    def __init__(self, app=None, page=None, function=None, urlparams=None):
        '''These variables are set by the process_view method above'''
        # the request object is set later by the middleware so the render methods work
        self.request = None

        # period and dash cannot be in python names, but we allow dash in app, dash in page, and dash/period in function
        self.app = app.replace('-', '_') if app is not None else None
        self.page = page.replace('-', '_') if page is not None else None
        if function and function != 'process_request':
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
            raise ValueError("RoutingData.render() can only be called after the view middleware is run. Check that `django_mako_plus.middleware` is in MIDDLEWARE.")
        dmp = apps.get_app_config('django_mako_plus')
        template_loader = dmp.engine.get_template_loader(self.app, subdir)
        template_adapter = template_loader.get_template(template)
        return getattr(template_adapter, 'render_to_response')(context=context, request=self.request, def_name=def_name, content_type=content_type, status=status, charset=charset)


    def render_to_string(self, template, context=None, def_name=None, subdir='templates'):
        '''App-specific render function that renders templates in the *current app*, attached to the request for convenience'''
        if self.request is None:
            raise ValueError("RoutingData.render() can only be called after the view middleware is run. Check that `django_mako_plus.middleware` is in MIDDLEWARE.")
        dmp = apps.get_app_config('django_mako_plus')
        template_loader = dmp.engine.get_template_loader(self.app, subdir)
        template_adapter = template_loader.get_template(template)
        return getattr(template_adapter, 'render')(context=context, request=self.request, def_name=def_name)
