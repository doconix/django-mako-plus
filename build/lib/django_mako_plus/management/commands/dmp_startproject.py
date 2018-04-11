from django.core.management.commands.startproject import Command as StartProjectCommand
from ..arg_override import ArgumentOverrideMixIn
import django_mako_plus
import os, os.path



class Command(ArgumentOverrideMixIn, StartProjectCommand):
    help = (
        "Creates a DMP project directory structure for the given project "
        "name in the current directory or optionally in the given directory."
    )

    def customize_template(self, action):
        # default to the online repo
        action.default = 'http://cdn.rawgit.com/doconix/django-mako-plus/master/project_template.zip'

        # attempt to use a local DMP install instead of the online repo as specified above
        if django_mako_plus.__file__:
            dmp_dir = os.path.dirname(django_mako_plus.__file__)
            template_dir = os.path.join(dmp_dir, 'project_template')
            if os.path.exists(template_dir):
                action.default = template_dir
