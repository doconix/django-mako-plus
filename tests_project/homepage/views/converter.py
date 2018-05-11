from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from django_mako_plus import view_function, parameter_converter

from homepage.models import IceCream, MyInt

from . import view_function

import decimal, datetime


###  View function endpoints  ###

@view_function
def process_request(request, s:str='', i:int=1, f:float=2, b:bool=False, ic:IceCream=None):
    return HttpResponse('parameter conversion tests')

@view_function
def more_testing(request, d:decimal.Decimal=None, dt:datetime.date=None, dttm:datetime.datetime=None, mi:MyInt=None):
    return HttpResponse('more parameter conversion tests')


###  Custom converter function  ###

class GeoLocation(object):
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude


@parameter_converter(GeoLocation)
def convert_geo_location(value, parameter):
    parts = value.split(',')
    if len(parts) < 2:
        raise ValueError('Both latitude and longitude are required')
    # the float constructor will raise ValueError if invalid
    return GeoLocation(float(parts[0]), float(parts[1]))


@view_function
def geo_location_endpoint(request, loc:GeoLocation):
    return HttpResponse('{}, {}'.format(loc.latitude, loc.longitude))


###  Class-based views  ###

class class_based(View):
    def get(self, request, s:str='', i:int=1, f:float=2, b:bool=False, ic:IceCream=None):
        return HttpResponse('Get was called.')


class class_based_decorated(View):
    # decorated
    @view_function
    def get(self, request, s:str='', i:int=1, f:float=2, b:bool=False, ic:IceCream=None):
        return HttpResponse('Get was called.')


class class_based_argdecorated(View):
    # decorated with arguments
    @view_function(a=1, b=2)
    def get(self, request, s:str='', i:int=1, f:float=2, b:bool=False, ic:IceCream=None):
        return HttpResponse('Get was called.')
