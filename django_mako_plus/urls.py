from django.apps import apps
try:
    from django.urls import re_path              # Django 2.x
except ImportError:  
    from django.conf.urls import url as re_path  # Django 1.x
from django.views.static import serve
from .router import route_request
from .registry import is_dmp_app
from .util import DMP_OPTIONS, get_dmp_app_configs
import os, os.path



#########################################################
###   The default DMP url patterns
### 
###   FYI, even though the valid python identifier is [_A-Za-z][_a-zA-Z0-9]*, 
###   I'm simplifying it to [_a-zA-Z0-9]+ because it works for our purposes


# start with the DMP web files - for development time
# at production, serve this directly with Nginx/IIS/etc. instead
urlpatterns = [
    re_path(r'^django_mako_plus/(?P<path>[^/]+)', serve, { 'document_root': os.path.join(apps.get_app_config('django_mako_plus').path, 'webroot') }, name='DMP webroot (for devel)'),
]

# app-specific patterns for each DMP-enabled app
for config in get_dmp_app_configs():
    # these are in order of specificity, with the most specific ones at the top
        urlpatterns.extend([
            # /app/page.function/urlparams
            re_path(r'^{}/(?P<dmp_router_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_router_function>[_a-zA-Z0-9\.\-]+)/?(?P<urlparams>.*?)/?$'.format(config.name), route_request, { 'dmp_router_app': config.name }, name='DMP /app/page.function'),
            # /app/page/urlparams
            re_path(r'^{}/(?P<dmp_router_page>[_a-zA-Z0-9\-]+)/?(?P<urlparams>.*?)/?$'.format(config.name), route_request, { 'dmp_router_app': config.name }, name='DMP /app/page'),
            # /app
            re_path(r'^{}/?$'.format(config.name), route_request, { 'dmp_router_app': config.name }, name='DMP /app'),
        ])

# if we have a default app, take over short urls
if DMP_OPTIONS.get('DEFAULT_APP') is not None: 
    urlpatterns.extend([
        # /page.function/urlparams
        re_path(r'^(?P<dmp_router_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_router_function>[_a-zA-Z0-9\.\-]*)/?(?P<urlparams>.*?)/?$', route_request, name='DMP /page.function'),
        # /page/urlparams
        re_path(r'^(?P<dmp_router_page>[_a-zA-Z0-9\-]+)/?(?P<urlparams>.*?)/?$', route_request, name='DMP /page'),
        # / with nothing else
        re_path(r'^$', route_request, name='DMP /'),
    ])

