from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View

from django_mako_plus import view_function
from django_mako_plus import RedirectException
from django_mako_plus import PermanentRedirectException
from django_mako_plus import InternalRedirectException
from django_mako_plus import JavascriptRedirectException

import datetime


###  Redirect exception  ###

@view_function
def redirect_exception(request):
    raise RedirectException('new_location')


###  Permanent redirect exception  ###

@view_function
def permanent_redirect_exception(request):
    raise PermanentRedirectException('permanent_new_location')


###  Permanent redirect exception  ###

@view_function
def javascript_redirect_exception(request):
    raise JavascriptRedirectException('javascript_new_location')


###  Internal redirect exceptions ###

@view_function
def internal_redirect_exception(request):
    raise InternalRedirectException('tests.views.redirects', 'internal_redirect_exception2')

@view_function
def bad_internal_redirect_exception(request):
    # tests nonexistent module
    raise InternalRedirectException('tests.non_existent', 'internal_redirect_exception2')

@view_function
def bad_internal_redirect_exception2(request):
    # tests nonexistent function
    raise InternalRedirectException('tests.views.redirects', 'nonexistent_function')

# should not be decorated with @view_function because a target of internal redirect
def internal_redirect_exception2(request):
    return HttpResponse('new_location2')

