from django.test import TestCase




class Tester(TestCase):

    def test_dmp_js(self):
        resp = self.client.get('/django_mako_plus/dmp-common.js')
        self.assertEqual(resp.status_code, 200)

    def test_app_page_function_urlparams(self):
        PATTERN_NAME = 'DMP /homepage/page.function/urlparams'
        resp = self.client.get('/homepage/index.process_request/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)
        resp = self.client.get('/homepage/index.process_request/1/2/3')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)

    def test_app_page_function(self):
        PATTERN_NAME = 'DMP /homepage/page.function'
        resp = self.client.get('/homepage/index.process_request/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)
        resp = self.client.get('/homepage/index.process_request')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)

    def test_app_page_urlparams(self):
        PATTERN_NAME = 'DMP /homepage/page/urlparams'
        resp = self.client.get('/homepage/index/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)
        resp = self.client.get('/homepage/index/1/2/3')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)

    def test_app_page(self):
        PATTERN_NAME = 'DMP /homepage/page'
        resp = self.client.get('/homepage/index/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)
        resp = self.client.get('/homepage/index')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)

    def test_app(self):
        PATTERN_NAME = 'DMP /homepage'
        resp = self.client.get('/homepage/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)
        resp = self.client.get('/homepage')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)

    def test_page_function_urlparams(self):
        PATTERN_NAME = 'DMP /<default app>/page.function/urlparams'
        resp = self.client.get('/index.process_request/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)
        resp = self.client.get('/index.process_request/1/2/3')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)

    def test_page_function(self):
        PATTERN_NAME = 'DMP /<default app>/page.function'
        resp = self.client.get('/index.process_request/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)
        resp = self.client.get('/index.process_request')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)

    def test_page_urlparams(self):
        PATTERN_NAME = 'DMP /<default app>/page/urlparams'
        resp = self.client.get('/index/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)
        resp = self.client.get('/index/1/2/3')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)

    def test_page(self):
        PATTERN_NAME = 'DMP /<default app>/page'
        resp = self.client.get('/index/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)
        resp = self.client.get('/index')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)

    def test_root(self):
        PATTERN_NAME = 'DMP /<default app>'
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.wsgi_request.resolver_match.url_name, PATTERN_NAME)
