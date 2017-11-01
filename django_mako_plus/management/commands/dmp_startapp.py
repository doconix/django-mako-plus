from django.core import management
from django.core.management.base import BaseCommand
import django_mako_plus
import os, os.path


class Command(BaseCommand):
    args = '<name>'
    help = 'Creates a new Django-Mako-Plus app.'
    can_import_settings = True
    missing_args_message = "You must provide an application name."


    def add_arguments(self, parser):
        # required argument for the app name
        parser.add_argument('appname', type=str, help='the name of the new app')


    def handle(self, *args, **options):
        # figure out the DMP app_template directory
        url = 'http://cdn.rawgit.com/doconix/django-mako-plus/master/app_template.zip'
        if django_mako_plus.__file__:
            dmp_dir = os.path.dirname(django_mako_plus.__file__)
            template_dir = os.path.join(dmp_dir, 'app_template')
            if os.path.exists(template_dir):
                url = template_dir

        # redirect
        self.stdout.write('Redirecting to startapp --template={} --extension=py,htm,html {}'.format(url, options['appname']))
        management.call_command('startapp', options['appname'], template=url, extension='py,htm,html')

