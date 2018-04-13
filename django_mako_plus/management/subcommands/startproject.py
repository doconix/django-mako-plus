from django.core.management.commands.startproject import Command as StartProjectCommand
from django_mako_plus.management.mixins import DMPCommandMixIn
from django_mako_plus.util import get_dmp_path

import os, os.path


NOT_SET = object()


class Command(DMPCommandMixIn, StartProjectCommand):
    help = (
        "Creates a DMP project directory structure for the given project "
        "name in the current directory or optionally in the given directory."
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)
        self.get_action_by_dest(parser, 'template').default = NOT_SET

    def handle(self, *args, **options):
        if options.get('template') is NOT_SET:
            # set the template to a DMP app
            options['template'] = 'http://cdn.rawgit.com/doconix/django-mako-plus/master/project_template.zip'
            # attempt to use a local DMP install instead of the online repo as specified above
            dmp_dir = get_dmp_path()
            if dmp_dir:
                template_dir = os.path.join(dmp_dir, 'project_template')
                if os.path.exists(template_dir):
                    options['template'] = template_dir

        # call the super
        StartProjectCommand.handle(self, *args, **options)

        self.message("""Project {name} created successfully!

What's next?
    1. cd {name}
    2. python3 manage.py dmp startapp homepage

""".format(name=options['name']))
