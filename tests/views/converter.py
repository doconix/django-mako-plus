from django.conf import settings
from django.http import HttpResponse
from django_mako_plus import view_function

from tests.models import IceCream, MyInt

import decimal, datetime


@view_function
def process_request(request, s:str='', i:int=1, f:float=2, b:bool=False, ic:IceCream=None):
    return HttpResponse('parameter conversion tests')


@view_function
def more_testing(request, d:decimal.Decimal, dt:datetime.date, dttm:datetime.datetime, mi:MyInt):
    return HttpResponse('more parameter conversion tests')


def test_converter(value, parameter, task):
    return task.kwargs['h1'] + task.kwargs['h2']

@view_function(converter=test_converter, h1='h1', h2='h2')
def custom_convert_function(request, s:str, i:int, f:float):
    return HttpResponse('{}-{}-{}'.format(s, i, f))
