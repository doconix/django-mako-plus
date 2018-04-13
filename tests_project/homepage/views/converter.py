from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from django_mako_plus import view_function

from homepage.models import IceCream, MyInt

import decimal, datetime



###  View function endpoints  ###

@view_function
def process_request(request, s:str='', i:int=1, f:float=2, b:bool=False, ic:IceCream=None):
    return HttpResponse('parameter conversion tests')

@view_function
def more_testing(request, d:decimal.Decimal=None, dt:datetime.date=None, dttm:datetime.datetime=None, mi:MyInt=None):
    return HttpResponse('more parameter conversion tests')


###  Custom converter endpoint  ###

def test_converter(value, parameter, task):
    return task.kwargs['h1'] + task.kwargs['h2']

@view_function(converter=test_converter, h1='h1', h2='h2')
def custom_convert_function(request, s:str, i:int, f:float):
    return HttpResponse('{}-{}-{}'.format(s, i, f))



###  Class-based endpoint  ###

class class_based(View):
    def get(self, request, i:int=None, f:float=None):
        return HttpResponse('Get was called.')

    def post(self, request, i:int=None, f:float=None):
        return HttpResponse('Post was called.')
