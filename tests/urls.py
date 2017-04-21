from django.conf.urls import url, include

urlpatterns = [
    # the DMP router - this should be the last line in the list
    url('', include('django_mako_plus.urls')),
]
