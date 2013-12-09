from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from mysite import settings

from django.contrib import admin
admin.autodiscover()

# specific urls that go to exact functions
urls = [
    '',
    # the standard admnistrator for django
    url(r'^admin/', include(admin.site.urls)),
]

# dynamic urls for just about anything - send to the central controller
urls.extend([
  # the base_app.controller handles every request - this line is the glue that connects Mako to Django
  url(r'^.*$', 'base_app.controller.route_request' ),

])

# this is the variable Django really wants
urlpatterns = patterns(*urls)

# set up the views for page not found and server errors
#handler404 = 'base.views.page_not_found_404.process_request'
#handler500 = 'base.views.server_error_500.process_request'