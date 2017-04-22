from django.apps import apps
from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.test import TestCase

from django_mako_plus.util import log
from django_mako_plus.util import get_dmp_instance
from django_mako_plus.template import MakoTemplateAdapter
from django_mako_plus.template import MakoTemplateLoader

import logging, os, os.path


class Tester(TestCase):

    @classmethod
    def setUpTestData(cls):
        # skip debug messages during testing
        cls.loglevel = log.getEffectiveLevel()
        log.setLevel(logging.WARNING)
        cls.tests_app = apps.get_app_config('tests')

    @classmethod
    def tearDownTestData(cls):
        # set log level back to normal
        log.setLevel(cls.loglevel)

    def test_is_dmp_app(self):
        self.assertTrue(get_dmp_instance().is_dmp_app('tests'))
        self.assertFalse(get_dmp_instance().is_dmp_app('nonexistent_app'))

    def test_from_string(self):
        template = get_dmp_instance().from_string('${ 2 + 2 }')
        self.assertIsInstance(template, MakoTemplateAdapter)
        self.assertEqual(template.render(None), "4")

    def test_get_template(self):
        template = get_dmp_instance().get_template('tests/basic.html')
        self.assertIsInstance(template, MakoTemplateAdapter)
        self.assertRaises(TemplateDoesNotExist, get_dmp_instance().get_template, 'tests/nonexistent_template.html')

    def test_get_template_loader(self):
        loader = get_dmp_instance().get_template_loader('tests', create=False)
        self.assertIsInstance(loader, MakoTemplateLoader)
        template = loader.get_template('basic.html')
        self.assertIsInstance(template, MakoTemplateAdapter)

    def test_get_template_loader_for_path(self):
        path = os.path.join(self.tests_app.path, 'templates')
        loader = get_dmp_instance().get_template_loader_for_path(path, use_cache=False)
        self.assertIsInstance(loader, MakoTemplateLoader)
        template = loader.get_template('basic.html')
        self.assertIsInstance(template, MakoTemplateAdapter)
