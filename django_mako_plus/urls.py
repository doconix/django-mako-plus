from django.apps import apps
from django.conf import settings
try:
    from django.urls import re_path              # Django 2.x
except ImportError:
    from django.conf.urls import url as re_path  # Django 1.x
from django.views.static import serve
from .router import dmp_path
import os, os.path


#########################################################
###   The default DMP url patterns
###
###   FYI, even though the valid python identifier is [_A-Za-z][_a-zA-Z0-9]*,
###   I'm simplifying it to [_a-zA-Z0-9]+ because it works for our purposes

# start with the DMP web files - for development time
# at production, serve this directly with Nginx/IIS/etc. instead
# there is no "if debug mode" statement here because the web server will serve the file at production before urls.py happens,
# but if this deployment step isn't done right, it will still work through this link
urlpatterns = [
    re_path(r'^django_mako_plus/(?P<path>[^/]+)', serve, { 'document_root': os.path.join(apps.get_app_config('django_mako_plus').path, 'webroot') }, name='DMP webroot (for devel)'),
]


# add a resolver for each app in the project directory
for config in apps.get_app_configs():
    if os.path.samefile(os.path.dirname(config.path), settings.BASE_DIR):
        urlpatterns.append(dmp_path(config.name))


# app-specific patterns for each DMP-enabled app
# for config in get_registered_apps():
    # # these are in order of specificity, with the most specific ones at the top
    # urlpatterns.extend([
    #     # /app/page.function/urlparams
    #     dmp_path(r'^{}/(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]+)/(?P<dmp_urlparams>.*?)/?$'.format(config.name), { 'dmp_app': config.name }, name='DMP /app/page.function/urlparams'),
    #     # /app/page.function
    #     dmp_path(r'^{}/(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]+)/?$'.format(config.name), { 'dmp_app': config.name }, name='DMP /app/page.function'),
    #     # /app/page/urlparams
    #     dmp_path(r'^{}/(?P<dmp_page>[_a-zA-Z0-9\-]+)/(?P<dmp_urlparams>.*?)/?$'.format(config.name), { 'dmp_app': config.name }, name='DMP /app/page/urlparams'),
    #     # /app/page
    #     dmp_path(r'^{}/(?P<dmp_page>[_a-zA-Z0-9\-]+)/?$'.format(config.name), { 'dmp_app': config.name }, name='DMP /app/page'),
    #     # /app
    #     dmp_path(r'^{}/?$'.format(config.name), { 'dmp_app': config.name }, name='DMP /app'),
    # ])

# # if we have a default app, take over short urls
# if DMP_OPTIONS['DEFAULT_APP']:
#     urlpatterns.extend([
#         # /page.function/urlparams
#         dmp_path(r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]*)/(?P<dmp_urlparams>.*?)/?$', { 'dmp_app': DMP_OPTIONS['DEFAULT_APP'] }, name='DMP /page.function/urlparams'),
#         # /page.function
#         dmp_path(r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]*)/?$', { 'dmp_app': DMP_OPTIONS['DEFAULT_APP'] }, name='DMP /page.function'),
#         # /page/urlparams
#         dmp_path(r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)/(?P<dmp_urlparams>.*?)/?$', { 'dmp_app': DMP_OPTIONS['DEFAULT_APP'] }, name='DMP /page/urlparams'),
#         # /page
#         dmp_path(r'^(?P<dmp_page>[_a-zA-Z0-9\-]+)/?$', { 'dmp_app': DMP_OPTIONS['DEFAULT_APP'] }, name='DMP /page'),
#         # / with nothing else
#         dmp_path(r'^$', { 'dmp_app': DMP_OPTIONS['DEFAULT_APP'] }, name='DMP /'),
#     ])
