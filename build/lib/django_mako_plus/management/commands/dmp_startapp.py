from django.core.management.commands.startapp import Command as StartAppCommand
from ..arg_override import ArgumentOverrideMixIn
import django_mako_plus
import os, os.path


class Command(ArgumentOverrideMixIn, StartAppCommand):
    help = (
        "Creates a DMP app directory structure for the given app name in "
        "the current directory or optionally in the given directory."
    )

    def customize_template(self, action):
        # default to the online repo
        action.default = 'http://cdn.rawgit.com/doconix/django-mako-plus/master/app_template.zip'

        # attempt to use a local DMP install instead of the online repo as specified above
        if django_mako_plus.__file__:
            dmp_dir = os.path.dirname(django_mako_plus.__file__)
            template_dir = os.path.join(dmp_dir, 'app_template')
            if os.path.exists(template_dir):
                action.default = template_dir

    def customize_extensions(self, action):
        self.default = [ 'py', 'htm', 'html' ]
