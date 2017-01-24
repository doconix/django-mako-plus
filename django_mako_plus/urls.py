from django.conf.urls import url
from django.urls.resolvers import RegexURLPattern
from django.urls.exceptions import Resolver404

from .router import route_request
from .util import get_dmp_instance



#########################################################
###   A custom url pattern that checks for DMP apps.

class DMPRegexPattern(RegexURLPattern):
    def resolve(self, path):
        '''
        First does the regular resolve.  If a match is found on the pattern,
        it then checks whether the named "dmp_router_app" variable is a
        DMP app.  If it is not a DMP app, it raises a Resolver404 indicating
        that we do not have a match.

        I'm doing this here in the url resolution instead of within route_request
        because I need to allow some overlapping patterns like /app and /page.

        An alternative to this would be to create a set of url patterns for each app.
        This would prevent this custom resolver, but it would significantly increase the
        number of url patterns (ugly).  And it would only include DMP apps that exist at
        compile time (and not any that are registered afterward, although I'm not sure
        when/if this would ever happen).

        I'm still not sure I made the right decision in choosing this small hack instead
        of the big set of normal url patterns.  But this is the decision for now.

        Any pattern wrapped in this class MUST have the named parameter: (?P<dmp_router_app>...)
        '''
        # let the super do its work
        rmatch = super().resolve(path)

        # if we have a match, check that the dmp_router_app is DMP-enabled
        if rmatch is not None and rmatch.kwargs['dmp_router_app'] not in get_dmp_instance().dmp_enabled_apps:
            raise Resolver404({'path': path})

        # return
        return rmatch




#########################################################
###   The default DMP url patterns

# FYI, even though the valid python identifier is [_A-Za-z][_a-zA-Z0-9]*, I'm simplifying it to [_a-zA-Z0-9]+ because it works for our purposes

urlpatterns = [
    # these are in order of specificity, with the most specific ones at the top

    # /app/page.function/urlparams
    DMPRegexPattern(r'^(?P<dmp_router_app>[_a-zA-Z0-9\-]+)/(?P<dmp_router_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_router_function>[_a-zA-Z0-9\.\-]+)/?(?P<urlparams>.*)$', route_request, name='DMP - /app/page.function'),

    # /app/page/urlparams
    DMPRegexPattern(r'^(?P<dmp_router_app>[_a-zA-Z0-9\-]+)/(?P<dmp_router_page>[_a-zA-Z0-9\-]+)/?(?P<urlparams>.*)$', route_request, name='DMP - /app/page'),

    # /app
    # FYI: /app/urlparams can't happen because the first urlparam would be captured as /app/page in the previous pattern
    DMPRegexPattern(r'^(?P<dmp_router_app>[_a-zA-Z0-9\-]+)/?$', route_request, name='DMP - /app'),

    # /page.function/urlparams
    url(r'^(?P<dmp_router_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_router_function>[_a-zA-Z0-9\.\-]*)/?(?P<urlparams>.*)$', route_request, name='DMP - /page.function'),

    # /page/urlparams
    url(r'^(?P<dmp_router_page>[_a-zA-Z0-9\-]+)/?(?P<urlparams>.*)$', route_request, name='DMP - /page'),

    # / with nothing else
    # FYI: /urlparams can't happen because it would be captured as /page in the previous pattern
    url(r'^$', route_request, name='DMP - /'),
]

