from django.test import TestCase

from django_mako_plus import render_template




class Tester(TestCase):

    def test_filters(self):
        html = render_template(None, 'homepage', 'filters.html', {
            'django_var': '::django::',
            'jinja2_var': '~~jinja2~~',
        })
        self.assertTrue('::django::' in html)
        self.assertTrue('~~jinja2~~' in html)
