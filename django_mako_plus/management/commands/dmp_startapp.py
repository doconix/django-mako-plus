from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import django_mako_plus

import os, os.path
from importlib import import_module


class Command(BaseCommand):
    args = '<name>'
    help = 'Creates a new Django-Mako-Plus app.'
    can_import_settings = True

    def handle(self, *args, **options):
        # ensure we have an app name
        if len(args) == 0:
            raise CommandError('you must specify an app name.')
        app_name = args[0]

        # Check that the app_name doesn't already exist
        try:
            import_module(app_name)
            raise CommandError("%r conflicts with the name of an existing Python module and cannot be used as an app name. Please try another name." % app_name)
        except ImportError:
            pass

        # Check that mako is importable
        try:
            import mako
        except ImportError:
            raise CommandError("The Mako templating engine cannot be imported.  Have you installed Mako yet?")

        # ensure we have a base directory
        try:
            if not os.path.isdir(settings.BASE_DIR):
                raise CommandError('Your settings.py BASE_DIR setting is not a valid directory.  Please check your settings.py file for the BASE_DIR variable.')
        except AttributeError:
            raise CommandError('Your settings.py file is missing the BASE_DIR setting. Aborting app creation.')

        # ensure we aren't overwriting an existing directory
        app_dir = os.path.join(os.path.join(os.path.abspath(settings.BASE_DIR), app_name))
        if os.path.exists(app_dir):
            raise CommandError('The new app directory already exists: %s.  Aborting app creation.' % app_dir)

        # create the directory structure by copying our app_template
        os.mkdir(app_dir)
        template_dir = os.path.join(os.path.abspath(os.path.dirname(django_mako_plus.__file__)), 'app_template')
        def copy_dir(root):
            for fname in os.listdir(root):
                # skip certain files
                if fname.startswith('.') or fname == '__pycache__':
                    continue

                # process this ile
                fpath = os.path.join(root, fname)
                newpath = os.path.join(app_dir, root[len(template_dir)+1:], fname)
                if os.path.isdir(fpath):
                    os.mkdir(newpath)
                    copy_dir(fpath)

                elif os.path.isfile(fpath):
                    fin = open(fpath)
                    fout = open(newpath, 'w')
                    fout.write(fin.read() % {
                      'app_name': app_name
                    })
                    fin.close()
                    fout.close()
        # start the copy process
        copy_dir(template_dir)

        self.stdout.write("App %s successfully created!  Don't forget to add your new app name (%s) to " % (app_name, app_name))
        self.stdout.write("the INSTALLED_APPS list in settings.py.  Once this is done, start your server and")
        self.stdout.write("go to http://localhost:8000/%s/index/ in a browser." % app_name)
