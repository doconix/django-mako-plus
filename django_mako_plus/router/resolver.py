from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ViewDoesNotExist
from django.core.checks.urls import check_resolver
from django.http import Http404
from django.urls import ResolverMatch, NoReverseMatch, Resolver404
from django.urls import URLResolver, URLPattern, re_path
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
from types import ModuleType
from collections import namedtuple



def dmp_app(app_name=None, kwargs=None, name=None, add_patterns=True):
    '''
    Registers the given app_name with DMP and adds a convention-based
    url resolver for it.

    This function should be used in urls.py in the same way that url()
    and re_path() are used.
    '''
    return AppResolver(app_name, default_args=kwargs, name=name, add_patterns=add_patterns)


def dmp_path(regex, kwargs, name):
    '''
    Creates a URL pattern for sending into dmp_app().  This function is
    automatically called by DMP to register the various convention-based
    patterns needed for DMP routing.  The only reason to use this function
    directly is to create a list of custom patterns that will be sent as
    a parameter to dmp_app().
    '''
    # this is a bit of a hack, but I'm trying to stay with Django's resolver/pattern
    # relationship and with Django's built-in functions as much as possibile.
    # Since Django's re_path() function requires a view, we need to create a no-op
    # even though DMP's AppResolver ignores it.
    def no_op_view(request):
        raise Http404()
    return re_path(regex, no_op_view, kwargs, name)



#################################################
###   The DMP Resolver


class AppResolver(URLResolver):
    '''
    Convention-based url resolver that implements DMP's app-aware view function finder.
    Do not use this class directly -- use dmp_app() above instead.
    '''
    def __init__(self, app_name=None, default_args=None, name=None, add_patterns=True):
        self.dmp = apps.get_app_config('django_mako_plus')
        if app_name is None:
            if not self.dmp.options['DEFAULT_APP']:
                raise ImproperlyConfigured('An app_name is required because DEFAULT_APP is empty - please use a '
                                           'valid app name or set the DMP default app in settings')
        else:
            self.dmp.register_app(app_name)
        self.app_name = app_name

        # the subpatterns for this app (dynamically create a urls.py module with patterns)
        urlconf_mod = ModuleType('urlconf')
        urlconf_mod.urlpatterns = self._generate_patterns() if add_patterns else []

        # call the super
        pat = RegexPattern(r'^{}/?'.format(app_name or ''), 'DMP /app for {}'.format(self.pretty_app_name), is_endpoint=False)
        kwargs = { 'dmp_app': app_name or self.dmp.options['DEFAULT_APP'] }
        if default_args:
            kwargs.update(default_args)
        super().__init__(pat, urlconf_mod, kwargs, app_name)


    def _generate_patterns(self):
        '''Creates the default patterns for an app'''
        patterns = []
        # /app/page.function/urlparams
        patterns.append(dmp_path(
            r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]+)/(?P<dmp_urlparams>.*?)/?$',
            {},
            'DMP /app/page.function/urlparams for {}'.format(self.pretty_app_name),
        ))
        # /app/page.function
        patterns.append(dmp_path(
            r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]+)/?$',
            {},
            'DMP /app/page.function for {}'.format(self.pretty_app_name),
        ))
        # /app/page/urlparams
        patterns.append(dmp_path(
            r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)/(?P<dmp_urlparams>.*?)/?$',
            {},
            'DMP /app/page/urlparams for {}'.format(self.pretty_app_name),
        ))
        # /app/page
        patterns.append(dmp_path(
            r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)/?$',
            {},
            'DMP /app/page for {}'.format(self.pretty_app_name),
        ))
        # /app
        patterns.append(dmp_path(
            r'^$',
            { 'dmp_page': self.dmp.options['DEFAULT_PAGE'] } if self.dmp.options['DEFAULT_PAGE'] else {},
            'DMP /app for {}'.format(self.pretty_app_name),
        ))
        return patterns


    @property
    def name(self):
        return self.pattern.name


    @property
    def pretty_app_name(self):
        return self.app_name or '<default app>'


    def resolve(self, path):
        path = str(path)  # path may be a reverse_lazy object
        tried = []

        # see if we have an /app match
        match = self.pattern.match(path)
        if not match:
            raise Resolver404({'path': path})

        # now check the subpatterns for page and urlparams
        new_path, args, kwargs = match
        for pattern in self.url_patterns:
            try:
                sub_match = pattern.resolve(new_path)
            except Resolver404 as e:
                sub_tried = e.args[0].get('tried')
                if sub_tried is not None:
                    tried.extend([pattern] + t for t in sub_tried)
                else:
                    tried.append([pattern])
                continue
            if not sub_match:
                tried.append([pattern])
                continue

            # we have a match!
            try:
                # Merge captured arguments in match with submatch
                sub_match_dict = dict(kwargs, **self.default_kwargs)
                # Update the sub_match_dict with the kwargs from the sub_match.
                sub_match_dict.update(sub_match.kwargs)
                # If there are *any* named groups, ignore all non-named groups.
                # Otherwise, pass all non-named arguments as positional arguments.
                sub_match_args = sub_match.args
                if not sub_match_dict:
                    sub_match_args = args + sub_match.args
                # now translate the subpattern args into a view function
                routing_data = RoutingData(
                    sub_match_dict.pop('dmp_app', None) or self.dmp.options['DEFAULT_APP'],
                    sub_match_dict.pop('dmp_page', None) or self.dmp.options['DEFAULT_PAGE'],
                    sub_match_dict.pop('dmp_function', None),
                    sub_match_dict.pop('dmp_urlparams', '').strip(),
                )
                # we got this!
                return ResolverMatch(
                    RequestViewWrapper(routing_data),
                    sub_match_args,
                    sub_match_dict,
                    sub_match.url_name,
                    [self.app_name] + sub_match.app_names,
                    [self.namespace] + sub_match.namespaces,
                )
            except ViewDoesNotExist as vdne:
                # we had a pattern match, but something went
                # wrong when getting a reference to the view function.
                # logging this case because the programmer needs info on what's wrong.
                log.debug('{}: {}'.format(pattern, vdne))
                tried.append([pattern])
                raise Resolver404({'tried': tried, 'path': new_path})

        # if we get here, no patterns matched
        raise Resolver404({'tried': tried, 'path': new_path})
