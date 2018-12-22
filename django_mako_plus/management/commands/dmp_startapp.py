from django.apps import apps
from django.core.management.commands.startapp import Command as StartAppCommand
from django_mako_plus.management.mixins import DMPCommandMixIn

import os, os.path


NOT_SET = object()


class Command(DMPCommandMixIn, StartAppCommand):
    help = (
        "Creates a DMP app directory structure for the given app name in "
        "the current directory or optionally in the given directory."
    )
    requires_system_checks = True

    def add_arguments(self, parser):
        super().add_arguments(parser)
        self.get_action_by_dest(parser, 'template').default = NOT_SET


    def handle(self, *args, **options):
        dmp = apps.get_app_config('django_mako_plus')
        if options.get('template') is NOT_SET:
            # set the template to a DMP app
            options['template'] = 'http://cdn.rawgit.com/doconix/django-mako-plus/master/app_template.zip'
            # attempt to use a local DMP install instead of the online repo as specified above
            dmp_dir = dmp.path
            if dmp_dir:
                template_dir = os.path.join(dmp_dir, 'app_template')
                if os.path.exists(template_dir):
                    options['template'] = template_dir

        # ensure we have the extensions we need
        options['extensions'] = list(set(options.get('extensions') + [ 'py', 'htm', 'html' ]))

        # call the super
        StartAppCommand.handle(self, *args, **options)

        self.message("""App {name} created successfully!

What's next?
    1. Add your new app to the list in settings.py:
        INSTALLED_APPS = [
            ...
            '{name}',
        ]
    2. python manage.py runserver
    3. Take a browser to http://localhost:8000/

""".format(name=options.get('name')))
