from django.conf import settings
from django.apps import apps
from django.core.management import execute_from_command_line
from django.core.management.base import CommandError
from django.test import TestCase
from django.template import TemplateDoesNotExist, TemplateSyntaxError

from django_mako_plus import get_template
from django_mako_plus.util import DMP_OPTIONS

from io import StringIO
import os, os.path, sys
import shutil

class Tester(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tests_app = apps.get_app_config('tests')


    def subcommand(self, *argv):
        # can't use Django's call_command because it doesn't deal with subparser options
        os.chdir(os.path.join(settings.BASE_DIR, 'tests'))
        buffer = StringIO()
        orig_stdout = sys.stdout
        sys.stdout = buffer
        try:
            execute_from_command_line([ 'manage.py', 'dmp' ] + list(argv))
        except CommandError as e:
            raise AssertionError('CommandError ocurred: {}'.format(e))
        except BaseException as e:
            raise AssertionError("Error calling command: {}".format(e)).with_traceback(sys.exc_info()[2])
        finally:
            sys.stdout = orig_stdout
        return buffer.getvalue()


    def test_cleanup(self):
        cache_dir = os.path.join(settings.BASE_DIR, 'tests', 'templates', DMP_OPTIONS['TEMPLATES_CACHE_DIR'])
        # compile a template
        template = get_template('tests', 'index.basic.html')
        self.assertTrue(os.path.exists(cache_dir))
        # run the cleanup command in trial mode
        result = self.subcommand('cleanup', '--trial-run')
        self.assertTrue('Cleaning up app: tests' in result)
        self.assertTrue(os.path.exists(cache_dir))
        # run the cleanup command
        result = self.subcommand('cleanup')
        self.assertTrue('Cleaning up app: tests' in result)
        self.assertFalse(os.path.exists(cache_dir))


    def test_collectstatic(self):
        settings.STATIC_ROOT = os.path.join(settings.BASE_DIR, 'tests/staticroot/')
        if os.path.exists(settings.STATIC_ROOT):
            shutil.rmtree(settings.STATIC_ROOT)
        try:
            result = self.subcommand('collectstatic')
            self.assertTrue(os.path.exists(os.path.join(settings.STATIC_ROOT, 'tests', 'media')))
            self.assertTrue(os.path.exists(os.path.join(settings.STATIC_ROOT, 'tests', 'scripts')))
            self.assertTrue(os.path.exists(os.path.join(settings.STATIC_ROOT, 'tests', 'scripts', 'base.js')))
            self.assertTrue(os.path.exists(os.path.join(settings.STATIC_ROOT, 'tests', 'styles')))
            self.assertTrue(os.path.exists(os.path.join(settings.STATIC_ROOT, 'tests', 'styles', 'base.css')))

        finally:
            if os.path.exists(settings.STATIC_ROOT):
                shutil.rmtree(settings.STATIC_ROOT)


    def test_makemessages(self):
        # TODO: the tests for this command need improvement
        result = self.subcommand('makemessages', '--ignore-template-errors', '--verbose')


    def test_startapp(self):
        appdir = os.path.join(settings.BASE_DIR, 'tests', 'teststartapp1')
        if os.path.exists(appdir):
            shutil.rmtree(appdir)
        try:
            result = self.subcommand('startapp', 'teststartapp1')
            self.assertTrue('teststartapp1 created successfully!' in result)
            self.assertTrue(os.path.exists(appdir))
        finally:
            if os.path.exists(appdir):
                shutil.rmtree(appdir)


    def test_startproject(self):
        appdir = os.path.join(settings.BASE_DIR, 'tests', 'testproject1')
        if os.path.exists(appdir):
            shutil.rmtree(appdir)
        try:
            result = self.subcommand('startproject', 'testproject1')
            self.assertTrue('testproject1 created successfully!' in result)
            self.assertTrue(os.path.exists(appdir))
        finally:
            if os.path.exists(appdir):
                shutil.rmtree(appdir)
