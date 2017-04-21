from django.apps import apps
from django.http import HttpResponse
from django.test import TestCase
from django.template import TemplateDoesNotExist, TemplateSyntaxError

from django_mako_plus import DefaultConverter, set_default_converter, get_default_converter
from django_mako_plus.util import log
from tests.models import IceCream
import logging
import os, os.path, datetime, decimal


class ConvenienceTest(TestCase):
    fixtures = [ 'ice_cream.json' ]

    @classmethod
    def setUp(cls):
        # skip debug messages during testing
        cls.loglevel = log.getEffectiveLevel()
        log.setLevel(logging.WARNING)
        set_default_converter(TestingConverter)

    @classmethod
    def tearDown(cls):
        # set log level back to normal
        log.setLevel(cls.loglevel)

    def test_default_converter(self):
        conv = get_default_converter()
        self.assertIsInstance(conv, TestingConverter)

    def test_empty_params(self):
        resp = self.client.get('/tests/converter/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        # urlparams should be empty
        self.assertFalse(req.urlparams)
        # test each parameter for its default
        self.assertEqual(req.converted_params['s'], '')
        self.assertEqual(req.converted_params['i'], 1)
        self.assertEqual(req.converted_params['f'], 2.0)
        self.assertFalse(req.converted_params['b'])
        self.assertIsNone(req.converted_params['ic'])

    def test_set_params(self):
        resp = self.client.get('/tests/converter/mystr/3/4/1/2/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.converted_params['s'], 'mystr')
        self.assertEqual(req.converted_params['i'], 3)
        self.assertEqual(req.converted_params['f'], 4.0)
        self.assertTrue(req.converted_params['b'])
        self.assertEqual(req.converted_params['ic'], IceCream.objects.get(pk=2))

    def test_boolean(self):
        resp = self.client.get('/tests/converter/s/3/4//-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertFalse(req.converted_params['b'])
        resp = self.client.get('/tests/converter/s/3/4/-/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertFalse(req.converted_params['b'])
        resp = self.client.get('/tests/converter/s/3/4/0/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertFalse(req.converted_params['b'])
        resp = self.client.get('/tests/converter/s/3/4/T/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertTrue(req.converted_params['b'])
        resp = self.client.get('/tests/converter/s/3/4/T/%20/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertTrue(req.converted_params['b'])

    def test_float(self):
        resp = self.client.get('/tests/converter/s/3/4/1/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.converted_params['f'], 4.0)
        resp = self.client.get('/tests/converter/s/3/4.0/1/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.converted_params['f'], 4.0)
        # bad value
        resp = self.client.get('/tests/converter/s/3/bad/1/-/')
        self.assertEqual(resp.status_code, 404)

    def test_int(self):
        resp = self.client.get('/tests/converter/s/3/4/1/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.converted_params['i'], 3)
        # bad value
        resp = self.client.get('/tests/converter/s/bad/4/1/-/')
        self.assertEqual(resp.status_code, 404)

    def test_model(self):
        # should be None
        resp = self.client.get('/tests/converter/s/3/4/1/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertIsNone(req.converted_params['ic'])
        # should pull id=1
        resp = self.client.get('/tests/converter/s/3/4/1/1/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.converted_params['ic'], IceCream.objects.get(id=1))
        # there is no id=5
        resp = self.client.get('/tests/converter/s/3/4/1/5/')
        self.assertEqual(resp.status_code, 404)
        # bad value
        resp = self.client.get('/tests/converter/s/3/4/1/abc/')
        self.assertEqual(resp.status_code, 404)

    def test_empty_more(self):
        resp = self.client.get('/tests/converter.more_testing/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        # urlparams should be empty
        self.assertFalse(req.urlparams)
        # test each parameter for its default
        self.assertIsNone(req.converted_params['d'])
        self.assertIsNone(req.converted_params['dt'])
        self.assertIsNone(req.converted_params['dttm'])

    def test_datetime(self):
        resp = self.client.get('/tests/converter.more_testing/1.23/2006-10-25/2006-10-25%2014:30:59/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertIsInstance(req.converted_params['dt'], datetime.date)
        self.assertIsInstance(req.converted_params['dttm'], datetime.datetime)
        # bad date
        resp = self.client.get('/tests/converter.more_testing/1.23/abcd/2006-10-25%2014:30:59/')
        self.assertEqual(resp.status_code, 404)
        # bad datetime
        resp = self.client.get('/tests/converter.more_testing/1.23/2006-10-25/abcd/')
        self.assertEqual(resp.status_code, 404)

    def test_decimal(self):
        resp = self.client.get('/tests/converter.more_testing/1.23/2006-10-25/2006-10-25%2014:30:59/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertIsInstance(req.converted_params['d'], decimal.Decimal)
        self.assertEqual(req.converted_params['d'], decimal.Decimal('1.23'))
        # bad decimal
        resp = self.client.get('/tests/converter.more_testing/abcd/2006-10-25/2006-10-25%2014:30:59/')
        self.assertEqual(resp.status_code, 404)
        # empty decimal
        resp = self.client.get('/tests/converter.more_testing/-/2006-10-25/2006-10-25%2014:30:59/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertIsNone(req.converted_params['d'])

    def test_override_int(self):
        set_default_converter(TestingConverter2)
        resp = self.client.get('/tests/converter/s/3/4/1/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.converted_params['i'], 300)




##########################################################
###   Small extension to the DefaultConverter that saves
###   the converted arguments so we can check them after a
###   call.

class TestingConverter(DefaultConverter):
    def __call__(self, value, parameter, task):
        value = super().__call__(value, parameter, task)
        if not hasattr(task.request, 'converted_params'):
            task.request.converted_params = {}
        task.request.converted_params[parameter.name] = value
        return value

# Override a type and to check a custom converter
class TestingConverter2(TestingConverter):
    @DefaultConverter.convert_method(int)
    def convert_int(self, value, parameter, task):
        if value is None:
            return None
        try:
            return parameter.type(value) + 100
        except Exception as e:
            log.info('Raising Http404 due to parameter conversion error: %s', e)
            raise Http404('Invalid parameter specified in the url')

