from django.test import TestCase




class Tester(TestCase):

    def test_view_function(self):
        # GET method
        resp = self.client.get('/homepage/index.basic/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        # POST method
        resp = self.client.post('/homepage/index.basic/1/2/3/')
        self.assertEqual(resp.status_code, 200)


    def test_does_not_exist(self):
        resp = self.client.get('/homepage/index.does_not_exist/1/2/3/')
        self.assertEqual(resp.status_code, 404)


    def test_bad_response(self):
        resp = self.client.get('/homepage/index.bad_response/1/2/3/')
        self.assertEqual(resp.status_code, 500)


    def test_class_based_view(self):
        # GET method
        resp = self.client.get('/homepage/index.class_based/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        # POST method
        resp = self.client.post('/homepage/index.class_based/1/2/3/')
        self.assertEqual(resp.status_code, 200)
        # PUT method (not defined in class)
        resp = self.client.put('/homepage/index.class_based/1/2/3/')
        self.assertEqual(resp.status_code, 405)  # method not allowed
