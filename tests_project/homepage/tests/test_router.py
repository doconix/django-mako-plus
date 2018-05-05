from django.test import TestCase




class Tester(TestCase):

    def test_view_function_get(self):
        # GET method
        resp = self.client.get('/homepage/index.basic/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp.urlparams[0], '1')
        self.assertEqual(req.dmp.urlparams[1], '2')
        self.assertEqual(req.dmp.urlparams[2], '3')


    def test_view_function_post(self):
        # POST method
        resp = self.client.post('/homepage/index.basic/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp.urlparams[0], '1')
        self.assertEqual(req.dmp.urlparams[1], '2')
        self.assertEqual(req.dmp.urlparams[2], '3')


    def test_does_not_exist(self):
        resp = self.client.get('/homepage/index.does_not_exist/1/2/3/')
        self.assertEqual(resp.status_code, 404)


    def test_bad_response(self):
        resp = self.client.get('/homepage/index.bad_response/1/2/3/')
        self.assertEqual(resp.status_code, 500)


    def test_class_based_get(self):
        # GET method
        resp = self.client.get('/homepage/index.class_based/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp.urlparams[0], '1')
        self.assertEqual(req.dmp.urlparams[1], '2')
        self.assertEqual(req.dmp.urlparams[2], '3')


    def test_class_based_post(self):
        # POST method
        resp = self.client.post('/homepage/index.class_based/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp.urlparams[0], '1')
        self.assertEqual(req.dmp.urlparams[1], '2')
        self.assertEqual(req.dmp.urlparams[2], '3')


    def test_class_based_invalid(self):
        # PUT method (not defined in class)
        resp = self.client.put('/homepage/index.class_based/1/2/3/')
        self.assertEqual(resp.status_code, 405)  # method not allowed


    def test_class_based_decorated(self):
        # GET method
        resp = self.client.get('/homepage/index.class_based_decorated/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp.urlparams[0], '1')
        self.assertEqual(req.dmp.urlparams[1], '2')
        self.assertEqual(req.dmp.urlparams[2], '3')


    def test_class_based_argdecorated(self):
        # GET method
        resp = self.client.get('/homepage/index.class_based_argdecorated/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        req = resp.wsgi_request
        self.assertEqual(req.dmp.urlparams[0], '1')
        self.assertEqual(req.dmp.urlparams[1], '2')
        self.assertEqual(req.dmp.urlparams[2], '3')
