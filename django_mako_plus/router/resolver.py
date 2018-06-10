from django.apps import apps
from django.conf import settings
from django.conf import urls as django_conf_urls
from django.core.exceptions import ImproperlyConfigured, ViewDoesNotExist
from django.urls import ResolverMatch, NoReverseMatch, Resolver404
from django.urls import URLResolver, URLPattern
from django.core.checks.urls import check_resolver
from django.urls.resolvers import RegexPattern
# try:
#     from django.urls import URLPattern                             # django 2.x
# except ImportError:
#     from django.urls import RegexURLPattern as URLPattern         # django 1.x
from django.utils.functional import cached_property

from ..util import log
from .data import RoutingData
from .decorators import RequestViewWrapper

from contextlib import contextmanager



def dmp_path(app_name, kwargs=None, name=None, patterns=None):
    '''
    Main function that should be called from urls.py.
    Adds a DMP convention-style URL resolver for an app.
    '''
    # register this app as a DMP app
    dmp = apps.get_app_config('django_mako_plus')
    if
    dmp.register_app(app_name)

    # create a resolver for this app
    return AppResolver(app_name, default_args=kwargs, name=name, patterns=patterns)


#########################################################
###  Pattern within an app resolver

class AppPattern(URLPattern):
    '''Convention-based pattern for a single regex'''

    def __init__(self, pattern, default_args=None, name=None):
        super().__init__(pattern, callback=None, default_args=default_args, name=name)



#########################################################
###  Resolver for an app


class AppResolverPattern(RegexPattern):
    '''Small extension for our AppResolver's pattern since Django expects it'''
    def __init__(self, resolver):
        self.resolver = resolver
        super().__init__('', name='', is_endpoint=False)
        self.name = self.redirected_name

    @property
    def redirected_name(self):
        return self.resolver.name

    def __repr__(self):
        return repr(self.resolver)

    def __str__(self):
        return str(self.resolver)


class AppResolver(URLResolver):
    '''
    Convention-based url resolver that implements DMP's app-aware view function finder.
    This is created when `dmp_path()` is called in urls.py.
    '''
    DEFAULT_PATTERNS = (
        # /app/page.function/urlparams
        (
            r'^{app_name}/(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]+)/(?P<dmp_urlparams>.*?)/?$',
            { 'dmp_app': '{app_name}' },
            'DMP /app/page.function/urlparams',
        ),
        # /app/page.function
        (
            r'^{app_name}/(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]+)/?$',
            { 'dmp_app': '{app_name}' },
            'DMP /app/page.function',
        ),
        # /app/page/urlparams
        (
            r'^{app_name}/(?P<dmp_page>[_a-zA-Z0-9\-]+)/(?P<dmp_urlparams>.*?)/?$',
            { 'dmp_app': '{app_name}' },
            'DMP /app/page/urlparams',
        ),
        # /app/page
        (
            r'^{app_name}/(?P<dmp_page>[_a-zA-Z0-9\-]+)/?$',
            { 'dmp_app': '{app_name}' },
            'DMP /app/page',
        ),
        # /app
        (
            r'^{app_name}/?$',
            { 'dmp_app': '{app_name}' },
            'DMP /app',
        ),
    )

    def __init__(self, app_name, default_args=None, name=None, patterns=None):
        self.dmp = apps.get_app_config('django_mako_plus')
        # initialize the patterns for this app
        self.patterns = patterns if patterns is not None else [
            AppPattern(
                RegexPattern(regex.format(app_name=app_name), name=name.format(app_name=app_name), is_endpoint=True),
                default_args={ k: v.format(app_name=app_name) for k, v in kwargs.items() },
                name=name.format(app_name=app_name),
            )
            for regex, kwargs, name in self.DEFAULT_PATTERNS
        ]
        self.app_name = app_name
        # call the super
        super().__init__(AppResolverPattern(self), app_name, default_kwargs=default_args, app_name=app_name, namespace=app_name)


    @property
    def name(self):
        return 'AppResolver for {}'.format(self.app_name)

    def __repr__(self):
        extra = ''
        current_pattern = getattr(self._local, 'current_pattern', None)
        if current_pattern is not None:
            extra += ', current pattern is {}'.format(current_pattern)
        match_error = getattr(self._local, 'match_error', None)
        if match_error is not None:
            extra += '; match resolution error is {}'.format(match_error)
        return '<{}{}>'.format(self.name, extra)

    def __str__(self):
        return repr(self)

    @property
    def url_patterns(self):
        # overriding because we do subpatterns differently than the super
        return self.patterns

    def check(self):
        warnings = []
        for pattern in self.url_patterns:
            warnings.extend(check_resolver(pattern))
        return warnings

    @contextmanager
    def stash_in_locals(self, pattern):
        '''Saves the pattern being matched (and any error) in locals for debug info to be printed'''
        try:
            self._local.match_error = None
            self._local.current_pattern = pattern
            yield
            self._local.current_pattern = None
        except ViewDoesNotExist as vdne:
            # save so (if DEBUG) Django can print using repr()
            self._local.match_error = vdne
            raise

    def resolve(self, path):
        path = str(path)
        try:
            for pat in self.patterns:
                with self.stash_in_locals(pat):
                    match = pat.resolve(path)
                    if match:
                        # the regex matched, so we are done matching our subpatterns
                        # now translate the subpattern args into a view function
                        routing_data = RoutingData(
                            match.kwargs.pop('dmp_app', None) or self.dmp.options['DEFAULT_APP'],
                            match.kwargs.pop('dmp_page', None) or self.dmp.options['DEFAULT_PAGE'],
                            match.kwargs.pop('dmp_function', None),
                            match.kwargs.pop('dmp_urlparams', '').strip(),
                        )
                        return ResolverMatch(
                            RequestViewWrapper(routing_data),
                            match.args,
                            match.kwargs,
                            pat.name,
                            [],
                        )
        except ViewDoesNotExist as vdne:
            # if we get here, we had a pattern match, but something went
            # wrong when getting a reference to the view function.
            # logging this case because the programmer needs info on what's wrong.
            log.debug(str(vdne))
            raise Resolver404({ 'path': path })
