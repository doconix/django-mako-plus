from django.conf.urls import url, include

urlpatterns = [
    # adds all DMP-enabled apps
    url('', include('django_mako_plus.urls')),
]
