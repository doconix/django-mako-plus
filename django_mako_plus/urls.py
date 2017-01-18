from django.conf.urls import url

from .router import route_request



urlpatterns = [
    # /app/page.function/
    url(r'^(?P<dmp_router_app>[^/]+)/(?P<dmp_router_page>[^/]+)\.(?P<dmp_router_function>[^/\.]+)/(?P<urlparams>.*)', route_request),

    # /app/page/ with default function process_request
    url(r'^(?P<dmp_router_app>[^/]+)/(?P<dmp_router_page>[^/]+)/(?P<urlparams>.*)', route_request),

    # wildcard: / or /app
    url(r'^(?P<urlparams>.*)$', route_request),

]

