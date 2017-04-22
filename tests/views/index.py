from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View

from django_mako_plus import view_function
from django_mako_plus import RedirectException, InternalRedirectException

from .. import dmp_render, dmp_render_to_string

import datetime



###  Function-based endpoints  ###

@view_function
def process_request(request):
    return dmp_render(request, 'index.html', {
        'current_time': datetime.datetime.now(),
    })


@view_function
def basic(request):
    return dmp_render(request, 'basic.html', {})


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


###  Redirect exception  ###

@view_function
def redirect_exception(request):
    raise RedirectException('new_location')


###  Internal redirect exceptions  ###

@view_function
def internal_redirect_exception(request):
    raise InternalRedirectException('tests.views.index', 'internal_redirect_exception2')

# internal redirect targets don't need @view_function (our code creates them, so security not needed)
def internal_redirect_exception2(request):
    return HttpResponse('new_location2')

# bad internal redirect target
@view_function
def bad_internal_redirect_exception(request):
    raise InternalRedirectException('tests.views.index', 'nonexistent_function')

@view_function
def bad_internal_redirect_exception2(request):
    raise InternalRedirectException('tests.non_existent', 'internal_redirect_exception2')

