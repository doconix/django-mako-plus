from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View

from django_mako_plus import view_function

import datetime




###  Function-based endpoints  ###

@view_function
def process_request(request):
    return request.dmp.render('index.html', {
        'current_time': datetime.datetime.now(),
    })


@view_function
def basic(request):
    return request.dmp.render('index.basic.html', {})


@view_function(a=1, b=2)
def decorated(request):
    return HttpResponse('This one is decorated')



###  Class-based endpoints  ###

class class_based(View):
    # not decorated (this is ok with class-based views)
    def get(self, request):
        return HttpResponse('Get was called.')

    def post(self, request):
        return HttpResponse('Post was called.')


class class_based_decorated(View):
    # decorated
    @view_function
    def get(self, request):
        return HttpResponse('Get was called.')


class class_based_argdecorated(View):
    # decorated with arguments
    @view_function(a=1, b=2)
    def get(self, request):
        return HttpResponse('Get was called.')


###  Doesn't return a response  ###

@view_function
def bad_response(request):
    return 'Should have been HttpResponse.'''
