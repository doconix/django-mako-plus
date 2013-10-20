from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

# specific urls that go to exact functions
urls = [
    '',
    # the standard admnistrator for django
    (r'^admin/', include(admin.site.urls)),
]

# items for debug mode only
if settings.DEVELOPMENT_SERVER:
  urls.extend([
    # static file on the site - for development server only.  Normally Nginx handles this before Django gets control (Django is proxied)
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',  { 'document_root': settings.STATIC_ROOT }),
  ])

# dynamic urls for just about anything - send to the central controller
urls.extend([
  # the mako_controller handles every request - this line is the glue that connects Mako to Django
  (r'^.*$', 'mako_controller.route_request' ),

])

# this is the variable Django really wants
urlpatterns = patterns(*urls)

# set up the views for page not found and server errors
#handler404 = 'base.views.page_not_found_404.process_request'
#handler500 = 'base.views.server_error_500.process_request'