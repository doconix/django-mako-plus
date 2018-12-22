from django.apps import apps
from django.template import TemplateDoesNotExist
from django.test import TestCase

from django_mako_plus.template import MakoTemplateAdapter
from django_mako_plus.template import MakoTemplateLoader

import os
import os.path


class Tester(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tests_app = apps.get_app_config('homepage')

    def test_from_string(self):
        dmp = apps.get_app_config('django_mako_plus')
        template = dmp.engine.from_string('${ 2 + 2 }')
        self.assertIsInstance(template, MakoTemplateAdapter)
        self.assertEqual(template.render(None), "4")

    def test_get_template(self):
        dmp = apps.get_app_config('django_mako_plus')
        template = dmp.engine.get_template('homepage/index.basic.html')
        self.assertIsInstance(template, MakoTemplateAdapter)
        self.assertRaises(TemplateDoesNotExist, dmp.engine.get_template, 'homepage/nonexistent_template.html')

    def test_get_template_loader(self):
        dmp = apps.get_app_config('django_mako_plus')
        loader = dmp.engine.get_template_loader('homepage', create=False)
        self.assertIsInstance(loader, MakoTemplateLoader)
        template = loader.get_template('index.basic.html')
        self.assertIsInstance(template, MakoTemplateAdapter)

    def test_get_template_loader_for_path(self):
        dmp = apps.get_app_config('django_mako_plus')
        path = os.path.join(self.tests_app.path, 'templates')
        loader = dmp.engine.get_template_loader_for_path(path, use_cache=False)
        self.assertIsInstance(loader, MakoTemplateLoader)
        template = loader.get_template('index.basic.html')
        self.assertIsInstance(template, MakoTemplateAdapter)
