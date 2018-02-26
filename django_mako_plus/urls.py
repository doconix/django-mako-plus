from django.apps import apps
try:
    from django.urls import re_path              # Django 2.x
except ImportError:
    from django.conf.urls import url as re_path  # Django 1.x
from django.views.static import serve
from .router import route_request
from .registry import get_dmp_apps
from .util import DMP_OPTIONS
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
for config in get_dmp_apps():
    # these are in order of specificity, with the most specific ones at the top
    urlpatterns.extend([
        # /app/page.function/urlparams
        re_path(r'^{}/(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]+)/?(?P<dmp_urlparams>.*?)/?$'.format(config.name), route_request, { 'dmp_app': config.name }, name='DMP /app/page.function'),
        # /app/page/urlparams
        re_path(r'^{}/(?P<dmp_page>[_a-zA-Z0-9\-]+)/?(?P<dmp_urlparams>.*?)/?$'.format(config.name), route_request, { 'dmp_app': config.name }, name='DMP /app/page'),
        # /app
        re_path(r'^{}/?$'.format(config.name), route_request, { 'dmp_app': config.name }, name='DMP /app'),
    ])

# if we have a default app, take over short urls
if DMP_OPTIONS['DEFAULT_APP']:
    urlpatterns.extend([
        # /page.function/urlparams
        re_path(r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]*)/?(?P<dmp_urlparams>.*?)/?$', route_request, name='DMP /page.function'),
        # /page/urlparams
        re_path(r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)/?(?P<dmp_urlparams>.*?)/?$', route_request, name='DMP /page'),
        # / with nothing else
        re_path(r'^$', route_request, name='DMP /'),
    ])
