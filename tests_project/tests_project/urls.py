from django.urls import include, path

urlpatterns = [
    # adds all DMP-enabled apps
    path('', include('django_mako_plus.urls')),
]
