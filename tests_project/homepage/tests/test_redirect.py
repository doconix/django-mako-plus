from django.test import TestCase




class Tester(TestCase):

    def test_redirect_exception(self):
        resp = self.client.get('/homepage/redirects.redirect_exception/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'new_location')


    def test_permanent_redirect_exception(self):
        resp = self.client.get('/homepage/redirects.permanent_redirect_exception/')
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp['Location'], 'permanent_new_location')


    def test_javascript_redirect_exception(self):
        resp = self.client.get('/homepage/redirects.javascript_redirect_exception/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(b'javascript_new_location' in resp.content)


    def test_internal_redirect_exception(self):
        resp = self.client.get('/homepage/redirects.internal_redirect_exception/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b'new_location2')


    def test_bad_internal_redirect_exception(self):
        resp = self.client.get('/homepage/redirects.bad_internal_redirect_exception/')
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get('/homepage/redirects.bad_internal_redirect_exception2/')
        self.assertEqual(resp.status_code, 404)
