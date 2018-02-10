from django.test import TestCase

from django_mako_plus.router import ViewFunctionRouter



class Tester(TestCase):

    # /app/page.function/urlparams
    def test_app_page_function(self):
        resp = self.client.get('/tests/index.basic/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp_app, 'tests')
        self.assertEqual(req.dmp_page, 'index')
        self.assertEqual(req.dmp_function, 'basic')
        self.assertEqual(req.dmp_module, 'tests.views.index')
        self.assertEqual(req.dmp_class, None)
        self.assertEqual(req.urlparams, [ '1', '2', '3' ])
        from tests.views import index
        self.assertIsInstance(req._dmp_router_callable, ViewFunctionRouter)
        self.assertEqual(req._dmp_router_callable.module, index)
        self.assertEqual(req._dmp_router_callable.function, index.basic)

    # /app/page/urlparams
    def test_app_page(self):
        resp = self.client.get('/tests/index/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp_app, 'tests')
        self.assertEqual(req.dmp_page, 'index')
        self.assertEqual(req.dmp_function, 'process_request')
        self.assertEqual(req.dmp_module, 'tests.views.index')
        self.assertEqual(req.dmp_class, None)
        self.assertEqual(req.urlparams, [ '1', '2', '3' ])
        from tests.views import index
        self.assertIsInstance(req._dmp_router_callable, ViewFunctionRouter)
        self.assertEqual(req._dmp_router_callable.module, index)
        self.assertEqual(req._dmp_router_callable.function, index.process_request)

    # /app
    def test_app(self):
        resp = self.client.get('/index/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp_app, 'tests')
        self.assertEqual(req.dmp_page, 'index')
        self.assertEqual(req.dmp_function, 'process_request')
        self.assertEqual(req.dmp_module, 'tests.views.index')
        self.assertEqual(req.dmp_class, None)
        self.assertEqual(req.urlparams, [])
        from tests.views import index
        self.assertIsInstance(req._dmp_router_callable, ViewFunctionRouter)
        self.assertEqual(req._dmp_router_callable.module, index)
        self.assertEqual(req._dmp_router_callable.function, index.process_request)

    # /page.function/urlparams
    def test_page_function(self):
        resp = self.client.get('/index.basic/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp_app, 'tests')
        self.assertEqual(req.dmp_page, 'index')
        self.assertEqual(req.dmp_function, 'basic')
        self.assertEqual(req.dmp_module, 'tests.views.index')
        self.assertEqual(req.dmp_class, None)
        self.assertEqual(req.urlparams, [ '1', '2', '3' ])
        from tests.views import index
        self.assertIsInstance(req._dmp_router_callable, ViewFunctionRouter)
        self.assertEqual(req._dmp_router_callable.module, index)
        self.assertEqual(req._dmp_router_callable.function, index.basic)

    # /page/urlparams
    def test_page(self):
        resp = self.client.get('/index/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp_app, 'tests')
        self.assertEqual(req.dmp_page, 'index')
        self.assertEqual(req.dmp_function, 'process_request')
        self.assertEqual(req.dmp_module, 'tests.views.index')
        self.assertEqual(req.dmp_class, None)
        self.assertEqual(req.urlparams, [ '1', '2', '3' ])
        from tests.views import index
        self.assertIsInstance(req._dmp_router_callable, ViewFunctionRouter)
        self.assertEqual(req._dmp_router_callable.module, index)
        self.assertEqual(req._dmp_router_callable.function, index.process_request)

    # / with nothing else
    def test_nothing_else(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp_app, 'tests')
        self.assertEqual(req.dmp_page, 'index')
        self.assertEqual(req.dmp_function, 'process_request')
        self.assertEqual(req.dmp_module, 'tests.views.index')
        self.assertEqual(req.dmp_class, None)
        self.assertEqual(req.urlparams, [])
        from tests.views import index
        self.assertIsInstance(req._dmp_router_callable, ViewFunctionRouter)
        self.assertEqual(req._dmp_router_callable.module, index)
        self.assertEqual(req._dmp_router_callable.function, index.process_request)
