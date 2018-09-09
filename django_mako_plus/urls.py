from django.apps import apps
from django.conf import settings
try:
    from django.urls import re_path              # Django 2.x
except ImportError:
    from django.conf.urls import url as re_path  # Django 1.x
from django.views.static import serve
from .router import app_resolver
import os, os.path


#########################################################
###   The default DMP url patterns
###
###   FYI, even though the valid python identifier is [_A-Za-z][_a-zA-Z0-9]*,
###   I'm simplifying it to [_a-zA-Z0-9]+ because it works for our purposes

app_name = 'django_mako_plus'
dmp = apps.get_app_config('django_mako_plus')
urlpatterns = []

# start with the DMP web files - for development time
# at production, serve this directly with Nginx/IIS/etc. instead
# there is no "if debug mode" statement here because the web server will serve the file at production before urls.py happens,
# but if this deployment step isn't done right, it will still work through this link
urlpatterns.append(re_path(
    r'^django_mako_plus/(?P<path>[^/]+)',
    serve,
    { 'document_root': os.path.join(apps.get_app_config('django_mako_plus').path, 'webroot') },
    name='DMP webroot (for devel)',
))

# add a DMP-style resolver for each app in the project directory
for config in apps.get_app_configs():
    if os.path.samefile(os.path.dirname(config.path), settings.BASE_DIR):
        urlpatterns.append(app_resolver(config.name))

# add a DMP-style resolver for the default app
if dmp.options['DEFAULT_APP']:
    try:
        apps.get_app_config(dmp.options['DEFAULT_APP'])
        urlpatterns.append(app_resolver())
    except LookupError:
        pass  # the default app in dmp's TEMPLATES entry isn't an installed app, so skip it
