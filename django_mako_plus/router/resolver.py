from django.conf import urls as django_conf_urls
from django.core.exceptions import ImproperlyConfigured
from django.urls import ResolverMatch, NoReverseMatch
try:
    from django.urls import URLPattern                             # django 2.x
except ImportError:
    from django.urls import RegexURLPattern as URLPattern         # django 1.x
from django.utils.functional import cached_property

from ..util import DMP_OPTIONS, log
from .data import RoutingData
from .decorators import RequestViewWrapper

import re



class DMPPattern(URLPattern):
    '''
    Our custom resolver that implements DMP's convention-based view function finder.
    '''
    # This class mimics django.urls.resolvers.URLResolver because it can return multiple routes
    # but some of the internals follow django.urls.resolvers.URLPattern

    def __init__(self, route, kwargs=None, name=None):
        self.route = route
        try:
            self._regex = re.compile(route)
        except Exception as e:
            raise ImproperlyConfigured('"%s" is not a valid regular expression: %s' % (route, e))
        self.default_kwargs = kwargs
        self.name = name

    @property
    def regex(self):
        # In Django 1.x, our super has this property.  So we have to override.
        # This method can be removed when Django 1.x support is dropped.
        return self._regex

    def __repr__(self):
        return '<{} {}{}>'.format(
            self.__class__.__name__,
            self.route,
            " [name='{}']".format(self.name) if self.name else '',
        )

    def resolve(self, path):
        path = str(path)                        # path may be a reverse_lazy object
        match = self._regex.search(path)
        if match:
            kwargs = match.groupdict()
            kwargs.update(self.default_kwargs)
            routing_data = RoutingData(
                kwargs.pop('dmp_app', None) or DMP_OPTIONS['DEFAULT_APP'],
                kwargs.pop('dmp_page', None) or DMP_OPTIONS['DEFAULT_PAGE'],
                kwargs.pop('dmp_function', None),
                kwargs.pop('dmp_urlparams', '').strip(),
            )
            if routing_data.callable is not None:
                return ResolverMatch(
                    RequestViewWrapper(routing_data),
                    (),
                    kwargs,
                    self.name,
                    [],
                )



# aliasing to `dmp_path` to look similar to the way Django's `path` and `re_path` look.
dmp_path = DMPPattern
