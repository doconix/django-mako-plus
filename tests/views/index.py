from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View

from django_mako_plus import view_function

import datetime



###  Function-based endpoints  ###

@view_function
def process_request(request):
    return request.dmp_render('index.html', {
        'current_time': datetime.datetime.now(),
    })


@view_function
def basic(request):
    return request.dmp_render('index.basic.html', {})


###  Class-based endpoint  ###

class class_based(View):
    def get(self, request):
        return HttpResponse('Get was called.')

    def post(self, request):
        return HttpResponse('Post was called.')



###  Doesn't return a response  ###

@view_function
def bad_response(request):
    return 'Should have been HttpResponse.'''

