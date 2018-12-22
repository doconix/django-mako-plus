from django.apps import apps
from django.test import TestCase
from django.test.utils import override_settings

class Tester(TestCase):

    def setUp(self):
        # resets all the Mako caches because we switch between debug and prod mode
        # during testing, and providers load differently for each
        dmp = apps.get_app_config('django_mako_plus')
        dmp.engine.template_loaders = {}


    @override_settings(DEBUG=True)
    def test_links(self):
        resp = self.client.get('/homepage/static_files/')
        self.assertEqual(resp.status_code, 200)
        # base
        self.assertTrue(b'/static/homepage/scripts/base.js' in resp.content)
        self.assertTrue(b'/static/homepage/styles/base.css' in resp.content)
        # static files
        self.assertTrue(b'homepage/scripts/static_files.js' in resp.content)
        self.assertTrue(b'homepage/styles/static_files.css' in resp.content)
        # jscontext output
        self.assertTrue(b'DMP_CONTEXT.set' in resp.content)
        self.assertTrue(b'data-context' in resp.content)
        self.assertTrue(b'key1' in resp.content)
        self.assertTrue(b'value1' in resp.content)
        self.assertTrue(b'key2' not in resp.content)
        self.assertTrue(b'value2' not in resp.content)
