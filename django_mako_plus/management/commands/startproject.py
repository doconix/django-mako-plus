from django.core.management.commands.startproject import Command as StartProjectCommand
from ..mixins import CommandOverrideMixIn, MessageMixIn
import django_mako_plus
import os, os.path



class Command(MessageMixIn, CommandOverrideMixIn, StartProjectCommand):
    help = (
        "Creates a DMP project directory structure for the given project "
        "name in the current directory or optionally in the given directory."
    )

    QUESTION = 'What kind of project would you like to create?'
    CHOICE_DMP = 'Create a Django project with DMP enabled `settings.py` and `urls.py` (default)'
    CHOICE_DJANGO = 'Create a standard Django project (you can add DMP later)'

    def dmp_handle(self, *args, **options):
        # set the template to a DMP app
        options['template'] = 'http://cdn.rawgit.com/doconix/django-mako-plus/master/project_template.zip'
        # attempt to use a local DMP install instead of the online repo as specified above
        if django_mako_plus.__file__:
            dmp_dir = os.path.dirname(django_mako_plus.__file__)
            template_dir = os.path.join(dmp_dir, 'project_template')
            if os.path.exists(template_dir):
                options['template'] = template_dir

        # call the super
        StartProjectCommand.handle(self, *args, **options)

        self.message()
        self.message('Project {} created successfully!'.format(options['name']))
        self.message()
