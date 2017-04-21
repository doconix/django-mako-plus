from django.conf import settings
from django.http import HttpResponse
from django_mako_plus import view_function

from tests.models import IceCream

import decimal, datetime


@view_function
def process_request(request, s:str='', i:int=1, f:float=2, b:bool=False, ic:IceCream=None):
    return HttpResponse('parameter conversion tests')


@view_function
def more_testing(request, d:decimal.Decimal, dt:datetime.date, dttm:datetime.datetime):
    return HttpResponse('more parameter conversion tests')
