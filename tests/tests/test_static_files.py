from django.test import TestCase


class Tester(TestCase):

    def test_links(self):
        resp = self.client.get('/tests/static_files/')
        self.assertEqual(resp.status_code, 200)
        # base
        self.assertTrue(b'/static/tests/scripts/base.js' in resp.content)
        self.assertTrue(b'/static/tests/styles/base.css' in resp.content)
        # static files
        self.assertTrue(b'tests/scripts/static_files.js' in resp.content)
        self.assertTrue(b'tests/styles/static_files.css' in resp.content)
        # jscontext output
        self.assertTrue(b'DMP_CONTEXT.set' in resp.content)
        self.assertTrue(b'data-context' in resp.content)
        self.assertTrue(b'key1' in resp.content)
        self.assertTrue(b'value1' in resp.content)
        self.assertTrue(b'key2' not in resp.content)
        self.assertTrue(b'value2' not in resp.content)
