from django.test import TestCase

from django_mako_plus.util import log
from homepage.models import IceCream, MyInt
import datetime
import decimal


class Tester(TestCase):
    fixtures = [ 'ice_cream.json' ]

    def test_empty_params(self):
        resp = self.client.get('/homepage/converter/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        # urlparams should be empty
        self.assertFalse(req.dmp.urlparams)
        # test each parameter for its default
        self.assertEqual(req.dmp.converted_params['s'], '')
        self.assertEqual(req.dmp.converted_params['i'], 1)
        self.assertEqual(req.dmp.converted_params['f'], 2.0)
        self.assertFalse(req.dmp.converted_params['b'])
        self.assertIsNone(req.dmp.converted_params['ic'])

    def test_set_params(self):
        resp = self.client.get('/homepage/converter/mystr/3/4/1/2/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp.converted_params['s'], 'mystr')
        self.assertEqual(req.dmp.converted_params['i'], 3)
        self.assertEqual(req.dmp.converted_params['f'], 4.0)
        self.assertTrue(req.dmp.converted_params['b'])
        self.assertEqual(req.dmp.converted_params['ic'], IceCream.objects.get(pk=2))

    def test_boolean(self):
        resp = self.client.get('/homepage/converter/s/3/4//-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertFalse(req.dmp.converted_params['b'])
        resp = self.client.get('/homepage/converter/s/3/4/-/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertFalse(req.dmp.converted_params['b'])
        resp = self.client.get('/homepage/converter/s/3/4/0/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertFalse(req.dmp.converted_params['b'])
        resp = self.client.get('/homepage/converter/s/3/4/T/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertTrue(req.dmp.converted_params['b'])
        resp = self.client.get('/homepage/converter/s/3/4/T/%20/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertTrue(req.dmp.converted_params['b'])

    def test_float(self):
        resp = self.client.get('/homepage/converter/s/3/4/1/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp.converted_params['f'], 4.0)
        resp = self.client.get('/homepage/converter/s/3/4.0/1/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp.converted_params['f'], 4.0)
        # bad value
        resp = self.client.get('/homepage/converter/s/3/bad/1/-/')
        self.assertEqual(resp.status_code, 404)

    def test_int(self):
        resp = self.client.get('/homepage/converter/s/3/4/1/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp.converted_params['i'], 3)
        # bad value
        resp = self.client.get('/homepage/converter/s/bad/4/1/-/')
        self.assertEqual(resp.status_code, 404)

    def test_model(self):
        # should be None
        resp = self.client.get('/homepage/converter/s/3/4/1/-/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertIsNone(req.dmp.converted_params['ic'])
        # should pull id=1
        resp = self.client.get('/homepage/converter/s/3/4/1/1/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp.converted_params['ic'], IceCream.objects.get(id=1))
        # there is no id=5
        resp = self.client.get('/homepage/converter/s/3/4/1/5/')
        self.assertEqual(resp.status_code, 404)
        # bad value
        resp = self.client.get('/homepage/converter/s/3/4/1/abc/')
        self.assertEqual(resp.status_code, 404)

    def test_empty_more(self):
        resp = self.client.get('/homepage/converter.more_testing/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        # urlparams should be empty
        self.assertFalse(req.dmp.urlparams)
        # test each parameter for its default
        self.assertIsNone(req.dmp.converted_params['d'])
        self.assertIsNone(req.dmp.converted_params['dt'])
        self.assertIsNone(req.dmp.converted_params['dttm'])

    def test_datetime(self):
        resp = self.client.get('/homepage/converter.more_testing/1.23/2026-10-25/2026-10-25%2014:30:59/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertIsInstance(req.dmp.converted_params['dt'], datetime.date)
        self.assertIsInstance(req.dmp.converted_params['dttm'], datetime.datetime)
        # bad date
        resp = self.client.get('/homepage/converter.more_testing/1.23/abcd/2026-10-25%2014:30:59/3/')
        self.assertEqual(resp.status_code, 404)
        # bad datetime
        resp = self.client.get('/homepage/converter.more_testing/1.23/2026-10-25/abcd/3/')
        self.assertEqual(resp.status_code, 404)

    def test_decimal(self):
        resp = self.client.get('/homepage/converter.more_testing/1.23/2026-10-25/2026-10-25%2014:30:59/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertIsInstance(req.dmp.converted_params['d'], decimal.Decimal)
        self.assertEqual(req.dmp.converted_params['d'], decimal.Decimal('1.23'))
        # bad decimal
        resp = self.client.get('/homepage/converter.more_testing/abcd/2026-10-25/2026-10-25%2014:30:59/3/')
        self.assertEqual(resp.status_code, 404)
        # empty decimal
        resp = self.client.get('/homepage/converter.more_testing/-/2026-10-25/2026-10-25%2014:30:59/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertIsNone(req.dmp.converted_params['d'])

    def test_geo_location_endpoint(self):
        resp = self.client.get('/homepage/converter.geo_location_endpoint/144.4,-24.6/')
        self.assertEqual(resp.status_code, 200)
        # hasattr is easier than importing the type
        req = resp.wsgi_request
        self.assertTrue(hasattr(req.dmp.converted_params['loc'], 'latitude'))
        self.assertTrue(hasattr(req.dmp.converted_params['loc'], 'longitude'))
