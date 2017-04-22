from django.test import TestCase

from django_mako_plus.router import ViewFunctionRouter
from django_mako_plus.util import log

import logging
import os, os.path


class Tester(TestCase):

    @classmethod
    def setUpTestData(cls):
        # skip debug messages during testing
        cls.loglevel = log.getEffectiveLevel()
        log.setLevel(logging.WARNING)

    @classmethod
    def tearDownTestData(cls):
        # set log level back to normal
        log.setLevel(cls.loglevel)


    def test_view_function(self):
        # GET method
        resp = self.client.get('/tests/index.basic/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        # POST method
        resp = self.client.post('/tests/index.basic/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request


    def test_does_not_exist(self):
        resp = self.client.get('/tests/index.does_not_exist/1/2/3/')
        self.assertEqual(resp.status_code, 404)
        req = resp.wsgi_request


    def test_bad_response(self):
        resp = self.client.get('/tests/index.bad_response/1/2/3/')
        self.assertEqual(resp.status_code, 500)
        req = resp.wsgi_request


    def test_class_based_view(self):
        # GET method
        resp = self.client.get('/tests/index.class_based/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        # POST method
        resp = self.client.post('/tests/index.class_based/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        # PUT method (not defined in class)
        resp = self.client.put('/tests/index.class_based/1/2/3/')
        self.assertEqual(resp.status_code, 405)  # method not allowed
        req = resp.wsgi_request
