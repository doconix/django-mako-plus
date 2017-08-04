from django.test import TestCase

from django_mako_plus.router import ViewFunctionRouter
from django_mako_plus.util import log

import logging
import os, os.path


class Tester(TestCase):

    def test_static_files(self):
        resp = self.client.get('/tests/static_files/')
        self.assertEqual(resp.status_code, 200)
        # base
        self.assertTrue(b'tests/scripts/base.js' in resp.content)
        self.assertFalse(b'+base.js+' in resp.content)
        self.assertTrue(b'+base.jsm+' in resp.content)
        self.assertTrue(b'tests/styles/base.css' in resp.content)
        self.assertFalse(b'+base.css+' in resp.content)
        self.assertTrue(b'+base.cssm+' in resp.content)
        # static files
        self.assertTrue(b'tests/scripts/static_files.js' in resp.content)
        self.assertFalse(b'+static_files.js+' in resp.content)
        self.assertTrue(b'+static_files.jsm+' in resp.content)
        self.assertTrue(b'tests/styles/static_files.css' in resp.content)
        self.assertFalse(b'+static_files.css+' in resp.content)
        self.assertTrue(b'+static_files.cssm+' in resp.content)

