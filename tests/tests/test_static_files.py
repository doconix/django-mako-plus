from django.test import TestCase




class Tester(TestCase):

    def test_links(self):
        resp = self.client.get('/tests/providers/')
        self.assertEqual(resp.status_code, 200)
        # base
        self.assertTrue(b'tests/scripts/base.js' in resp.content)
        self.assertFalse(b'+base.js+' in resp.content)
        self.assertTrue(b'+base.jsm+' in resp.content)
        self.assertTrue(b'tests/styles/base.css' in resp.content)
        self.assertFalse(b'+base.css+' in resp.content)
        self.assertTrue(b'+base.cssm+' in resp.content)
        # static files
        self.assertTrue(b'tests/scripts/providers.js' in resp.content)
        self.assertFalse(b'+providers.js+' in resp.content)
        self.assertTrue(b'+providers.jsm+' in resp.content)
        self.assertTrue(b'tests/styles/providers.css' in resp.content)
        self.assertFalse(b'+providers.css+' in resp.content)
        self.assertTrue(b'+providers.cssm+' in resp.content)

