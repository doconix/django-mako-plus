from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View

from django_mako_plus import view_function, jscontext


@view_function
def process_request(request):
    return request.render('static_files.html', {
        jscontext('key1'): 'value1',
        'key2': 'value2',
    })

