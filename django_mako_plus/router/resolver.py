from django.apps import apps
from django.core.exceptions import ViewDoesNotExist
from django.http import Http404
from django.urls import ResolverMatch
from django.urls.exceptions import Resolver404
try:
    from django.urls import re_path              # Django 2.x
    from django.urls import URLPattern
    from django.urls import include
    from django.urls.resolvers import RegexPattern
except ImportError:
    from django.conf.urls import url as re_path  # Django 1.x
    from django.urls import RegexURLPattern as URLPattern
    from django.conf.urls import include
    RegexPattern = None

from ..util import merge_dicts, log
from .data import RoutingData
from .decorators import RequestViewWrapper

from collections import namedtuple



##################################################
###  DMP-style resolver for an app


def app_resolver(app_name=None, pattern_kwargs=None, name=None):
    '''
    Registers the given app_name with DMP and adds convention-based
    url patterns for it.

    This function is meant to be called in a project's urls.py.
    '''
    urlconf = URLConf(app_name, pattern_kwargs)
    resolver = re_path(
        '^{}/?'.format(app_name) if app_name is not None else '',
        include(urlconf),
        name=urlconf.app_name,
    )
    # this next line is a workaround for Django's URLResolver class not having
    # a `name` attribute, which is expected in Django's technical_404.html.
    resolver.name = getattr(resolver, 'name', name or app_name)
    return resolver


class URLConf(object):
    '''
    Mimics a urls.py module for an app by holding a list of url patterns.
    This is run through Django's include() function to create a resolver.

    Call `app_resolver()` to instantiate this class.  Do not create it directly.
    '''
    def __init__(self, app_name=None, pattern_kwargs=None):
        self._app_name = app_name
        self.app_name = self._app_name or '<default app>'
        self.name = self.app_name
        dmp = apps.get_app_config('django_mako_plus')
        dmp.register_app(self._app_name)
        self.urlpatterns = dmp_paths_for_app(self._app_name, pattern_kwargs, self.app_name)


def dmp_paths_for_app(app_name, pattern_kwargs=None, pretty_app_name=None):
    '''Utility function that creates the default patterns for an app'''
    dmp = apps.get_app_config('django_mako_plus')
    # Because these patterns are subpatterns within the app's resolver,
    # we don't include the /app/ in the pattern -- it's already been
    # handled by the app's resolver.
    #
    # Also note how the each pattern below defines the four kwargs--
    # either as 1) a regex named group or 2) in kwargs.
    return [
        # page.function/urlparams
        dmp_path(
            r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]+)/(?P<dmp_urlparams>.+?)/?$',
            merge_dicts({
                'dmp_app': app_name or dmp.options['DEFAULT_APP'],
            }, pattern_kwargs),
            'DMP /{}/page.function/urlparams'.format(pretty_app_name),
            app_name,
        ),

        # page.function
        dmp_path(
            r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]+)/?$',
            merge_dicts({
                'dmp_app': app_name or dmp.options['DEFAULT_APP'],
                'dmp_urlparams': '',
            }, pattern_kwargs),
            'DMP /{}/page.function'.format(pretty_app_name),
            app_name,
        ),

        # page/urlparams
        dmp_path(
            r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)/(?P<dmp_urlparams>.+?)/?$',
            merge_dicts({
                'dmp_app': app_name or dmp.options['DEFAULT_APP'],
                'dmp_function': 'process_request',
            }, pattern_kwargs),
            'DMP /{}/page/urlparams'.format(pretty_app_name),
            app_name,
        ),

        # page
        dmp_path(
            r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)/?$',
            merge_dicts({
                'dmp_app': app_name or dmp.options['DEFAULT_APP'],
                'dmp_function': 'process_request',
                'dmp_urlparams': '',
            }, pattern_kwargs),
            'DMP /{}/page'.format(pretty_app_name),
            app_name,
        ),

        # empty
        dmp_path(
            r'^$',
            merge_dicts({
                'dmp_app': app_name or dmp.options['DEFAULT_APP'],
                'dmp_function': 'process_request',
                'dmp_urlparams': '',
                'dmp_page': dmp.options['DEFAULT_PAGE'],
            }, pattern_kwargs),
            'DMP /{}'.format(pretty_app_name),
            app_name,
        ),
    ]




#############################################
###  DMP-style pattern


def dmp_path(regex, kwargs=None, name=None, app_name=None):
    '''
    Creates a DMP-style, convention-based pattern that resolves
    to various view functions based on the 'dmp_page' value.

    The following should exist as 1) regex named groups or
    2) items in the kwargs dict:
        dmp_app         Should resolve to a name in INSTALLED_APPS.
                        If missing, defaults to DEFAULT_APP.
        dmp_page        The page name, which should resolve to a module:
                        project_dir/{dmp_app}/views/{dmp_page}.py
                        If missing, defaults to DEFAULT_PAGE.
        dmp_function    The function name (or View class name) within the module.
                        If missing, defaults to 'process_request'
        dmp_urlparams   The urlparams string to parse.
                        If missing, defaults to ''.

    The reason for this convenience function is to be similar to
    Django functions like url(), re_path(), and path().
    '''
    return PagePattern(regex, kwargs, name, app_name)


class PagePattern(URLPattern):
    '''
    Creates a DMP-style, convention-based pattern that resolves
    to various view functions based on the 'dmp_page' value.
    '''
    def __init__(self, regex, default_args=None, name=None, app_name=None):
        self.dmp = apps.get_app_config('django_mako_plus')
        if app_name or self.dmp.options['DEFAULT_APP']:
            self.dmp.register_app(app_name)
        default_args = merge_dicts({ 'dmp_app': app_name or self.dmp.options['DEFAULT_APP'] }, default_args)
        if isinstance(regex, str) and RegexPattern is not None:
            regex = RegexPattern(regex, name=name, is_endpoint=True)
        # this is a bit of a hack, but the super constructor needs
        # a view function. Our resolve() function ignores this view function
        # so we'll just creeate a no-op placeholder so super is happy.
        def no_op_view(request):
            raise Http404()
        super().__init__(regex, no_op_view, default_args, name=name)


    def resolve(self, path):
        '''
        Different from Django, this method matches by /app/page/ convention
        using its pattern.  The pattern should create keyword arguments for
        dmp_app, dmp_page.
        '''
        match = super().resolve(path)
        if match:
            try:
                routing_data = RoutingData(
                    match.kwargs.pop('dmp_app', None) or self.dmp.options['DEFAULT_APP'],
                    match.kwargs.pop('dmp_page', None) or self.dmp.options['DEFAULT_PAGE'],
                    match.kwargs.pop('dmp_function', None) or 'process_request',
                    match.kwargs.pop('dmp_urlparams', '').strip(),
                )
                return ResolverMatch(
                    RequestViewWrapper(routing_data),
                    match.args,
                    match.kwargs,
                    match.url_name,
                )
            except ViewDoesNotExist as vdne:
                # we had a pattern match, but we couldn't get a callable using kwargs from the pattern
                # create a "pattern" so the programmer can see what happened
                # this is a hack, but the resolver error page doesn't give other options.
                # the sad face is to catch the dev's attention in Django's printout
                msg = "◉︵◉ Pattern matched, but discovery failed: {}".format(vdne)
                log.debug("%s %s", match.url_name, msg)
                raise Resolver404({
                    # this is a bit convoluted, but it makes the PatternStub work with Django 1.x and 2.x
                    'tried': [[ PatternStub(match.url_name, msg, PatternStub(match.url_name, msg, None)) ]],
                    'path': path,
                })



from collections import namedtuple
PatternStub = namedtuple('PatternStub', [ 'name', 'pattern', 'regex' ])
