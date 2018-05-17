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
        cls.tests_app = apps.get_app_config('homepage')


    def subcommand(self, *argv):
        # can't use Django's call_command because it doesn't deal with subparser options
        buffer = StringIO()
        orig_stdout = sys.stdout
        sys.stdout = buffer
        try:
            execute_from_command_line([ 'manage.py', 'dmp' ] + list(argv))
        except CommandError as e:
            raise AssertionError('CommandError ocurred: {}'.format(e))
        except Exception as e:
            raise AssertionError("Error calling command: {}".format(e)).with_traceback(sys.exc_info()[2])
        finally:
            sys.stdout = orig_stdout
        return buffer.getvalue()


    def test_cleanup(self):
        cache_dir = os.path.join(settings.BASE_DIR, 'homepage', 'templates', DMP_OPTIONS['TEMPLATES_CACHE_DIR'])
        # compile a template
        template = get_template('homepage', 'index.basic.html')
        self.assertTrue(os.path.exists(cache_dir))
        # run the cleanup command in trial mode
        result = self.subcommand('cleanup', '--trial-run')
        self.assertTrue('Cleaning up app: homepage' in result)
        self.assertTrue(os.path.exists(cache_dir))
        # run the cleanup command
        result = self.subcommand('cleanup')
        self.assertTrue('Cleaning up app: homepage' in result)
        self.assertFalse(os.path.exists(cache_dir))


    def test_collectstatic(self):
        settings.STATIC_ROOT = os.path.join(settings.BASE_DIR, 'homepage/staticroot/')
        if os.path.exists(settings.STATIC_ROOT):
            shutil.rmtree(settings.STATIC_ROOT)
        try:
            result = self.subcommand('collectstatic')
            self.assertTrue(os.path.exists(os.path.join(settings.STATIC_ROOT, 'homepage', 'media')))
            self.assertTrue(os.path.exists(os.path.join(settings.STATIC_ROOT, 'homepage', 'scripts')))
            self.assertTrue(os.path.exists(os.path.join(settings.STATIC_ROOT, 'homepage', 'scripts', 'base.js')))
            self.assertTrue(os.path.exists(os.path.join(settings.STATIC_ROOT, 'homepage', 'styles')))
            self.assertTrue(os.path.exists(os.path.join(settings.STATIC_ROOT, 'homepage', 'styles', 'base.css')))

        finally:
            if os.path.exists(settings.STATIC_ROOT):
                shutil.rmtree(settings.STATIC_ROOT)


    def test_makemessages(self):
        # TODO: the tests for this command need improvement
        result = self.subcommand('makemessages', '--ignore-template-errors', '--verbose')


    def test_startapp(self):
        appdir = os.path.join(settings.BASE_DIR, 'teststartapp1')
        if os.path.exists(appdir):
            shutil.rmtree(appdir)
        try:
            result = self.subcommand('startapp', 'teststartapp1')
            self.assertTrue('teststartapp1 created successfully!' in result)
            self.assertTrue(os.path.exists(appdir))
            self.assertTrue(os.path.isdir(os.path.join(appdir, 'media')))
            self.assertTrue(os.path.isdir(os.path.join(appdir, 'scripts')))
            self.assertTrue(os.path.isdir(os.path.join(appdir, 'styles')))
            self.assertTrue(os.path.isdir(os.path.join(appdir, 'templates')))
            self.assertTrue(os.path.isdir(os.path.join(appdir, 'views')))
            self.assertTrue(os.path.exists(os.path.join(appdir, 'apps.py')))
            with open(os.path.join(appdir, 'apps.py')) as fin:
                self.assertTrue('teststartapp1' in fin.read())
        finally:
            if os.path.exists(appdir):
                shutil.rmtree(appdir)


    def test_startproject(self):
        projdir = os.path.join(settings.BASE_DIR, 'testproject1')
        if os.path.exists(projdir):
            shutil.rmtree(projdir)
        try:
            result = self.subcommand('startproject', 'testproject1')
            self.assertTrue('testproject1 created successfully!' in result)
            self.assertTrue(os.path.exists(projdir))
            self.assertTrue(os.path.isdir(os.path.join(projdir, 'testproject1')))
            with open(os.path.join(projdir, 'manage.py')) as fin:
                self.assertTrue('testproject1.settings' in fin.read())
            self.assertTrue(os.path.exists(os.path.join(projdir, 'testproject1', 'settings.py')))
            self.assertTrue(os.path.exists(os.path.join(projdir, 'testproject1', 'urls.py')))
            self.assertTrue(os.path.exists(os.path.join(projdir, 'testproject1', 'wsgi.py')))
        finally:
            if os.path.exists(projdir):
                shutil.rmtree(projdir)


    def test_webpack(self):
        # TODO: the tests for this command need improvement
        entrypath = os.path.join(settings.BASE_DIR, 'homepage', 'scripts', '__entry__.js')
        if os.path.exists(entrypath):
            os.remove(entrypath)
        try:
            result = self.subcommand('webpack', 'homepage', '--verbose')
            self.assertTrue(os.path.exists(os.path.exists(entrypath)))
        finally:
            if os.path.exists(entrypath):
                os.remove(entrypath)
