from django.apps import apps
from django.test import TestCase
from django.template import TemplateDoesNotExist, TemplateSyntaxError

from django_mako_plus import get_template_loader
from django_mako_plus import get_template
from django_mako_plus import render_template
from django_mako_plus import get_template_loader_for_path
from django_mako_plus import get_template_for_path
from django_mako_plus import render_template_for_path
from django_mako_plus.template import MakoTemplateLoader, MakoTemplateAdapter

import os, os.path


class Tester(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tests_app = apps.get_app_config('homepage')
        cls.errors_app = apps.get_app_config('errorsapp')

    def test_get_template_loader(self):
        # should succeed
        loader = get_template_loader('homepage')
        self.assertIsInstance(loader, MakoTemplateLoader)
        # should fail with LookupError
        self.assertRaises(LookupError, get_template_loader, 'nonexistent_app')

    def test_get_template(self):
        # should succeed
        template = get_template('homepage', 'index.basic.html')
        self.assertIsInstance(template, MakoTemplateAdapter)
        # these should fail
        self.assertRaises(LookupError, get_template, 'nonexistent_app', 'index.basic.html')
        self.assertRaises(TemplateDoesNotExist, get_template, 'errorsapp', 'nonexistent_template.html')
        self.assertRaises(TemplateSyntaxError, get_template, 'errorsapp', 'syntax_error.html')

    def test_render_template(self):
        # should succeed
        html = render_template(None, 'homepage', 'index.basic.html')
        self.assertIsInstance(html, str)
        # these should fail
        self.assertRaises(LookupError, render_template, None, 'nonexistent_app', 'index.basic.html')
        self.assertRaises(TemplateDoesNotExist, render_template, None, 'errorsapp', 'nonexistent_template.html')
        self.assertRaises(TemplateSyntaxError, render_template, None, 'errorsapp', 'syntax_error.html')

    def test_def_name(self):
        # test a def name
        html = render_template(None, 'homepage', 'index.basic.html', def_name='content')
        self.assertIsInstance(html, str)
        # this def doesn't exist
        self.assertRaises(AttributeError, render_template, None, 'homepage', 'index.basic.html', def_name='nonexistent_def')

    def test_get_template_loader_for_path(self):
        path = os.path.join(self.tests_app.path, 'templates')
        loader = get_template_loader_for_path(path, use_cache=False)
        self.assertIsInstance(loader, MakoTemplateLoader)
        loader = get_template_loader_for_path(path, use_cache=True)
        self.assertIsInstance(loader, MakoTemplateLoader)

    def test_get_template_for_path(self):
        path = os.path.join(self.tests_app.path, 'templates', 'index.basic.html')
        bad_path = os.path.join(self.tests_app.path, 'templates', 'nonexistent_template.html')
        bad_path2 = os.path.join(self.tests_app.path, 'nonexistent_dir', 'index.basic.html')
        # should succeed
        template = get_template_for_path(path, use_cache=False)
        self.assertIsInstance(template, MakoTemplateAdapter)
        template = get_template_for_path(path, use_cache=True)
        self.assertIsInstance(template, MakoTemplateAdapter)
        # these should fail
        self.assertRaises(TemplateDoesNotExist, get_template_for_path, bad_path)
        self.assertRaises(TemplateDoesNotExist, get_template_for_path, bad_path2)

    def test_render_template_for_path(self):
        path = os.path.join(self.tests_app.path, 'templates', 'index.basic.html')
        bad_path = os.path.join(self.errors_app.path, 'templates', 'nonexistent_template.html')
        bad_path2 = os.path.join(self.errors_app.path, 'nonexistent_dir', 'index.basic.html')
        bad_syntax_path = os.path.join(self.errors_app.path, 'templates', 'syntax_error.html')
        # should succeed
        html = render_template_for_path(None, path, use_cache=False)
        self.assertIsInstance(html, str)
        template = render_template_for_path(None, path, use_cache=True)
        self.assertIsInstance(html, str)
        # these should fail
        self.assertRaises(TemplateDoesNotExist, render_template_for_path, None, bad_path, {})
        self.assertRaises(TemplateDoesNotExist, render_template_for_path, None, bad_path2, {})
        self.assertRaises(TemplateSyntaxError, render_template_for_path, None, bad_syntax_path, {})
