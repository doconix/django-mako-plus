from django.core.management.commands.startapp import Command as StartAppCommand
from ..mixins import CommandOverrideMixIn, MessageMixIn
import django_mako_plus
import os, os.path



class Command(MessageMixIn, CommandOverrideMixIn, StartAppCommand):
    help = (
        "Creates a DMP app directory structure for the given app name in "
        "the current directory or optionally in the given directory."
    )
    QUESTION = 'What kind of app would you like to create?'
    CHOICE_DMP = 'Create a DMP-oriented app structure (default)'
    CHOICE_DJANGO = 'Create a standard Django app structure'

    def dmp_handle(self, *args, **options):
        # set the template to a DMP app
        options['template'] = 'http://cdn.rawgit.com/doconix/django-mako-plus/master/app_template.zip'
        # attempt to use a local DMP install instead of the online repo as specified above
        if django_mako_plus.__file__:
            dmp_dir = os.path.dirname(django_mako_plus.__file__)
            template_dir = os.path.join(dmp_dir, 'app_template')
            if os.path.exists(template_dir):
                options['template'] = template_dir

        # set the extensions
        options['extensions'] = [ 'py', 'htm', 'html' ]

        # call the super
        StartAppCommand.handle(self, *args, **options)

        self.message()
        self.message("App {} created successfully!  Don't forget to add it to your INSTALLED_APPS in settings.py.".format(options['name']))
        self.message()
