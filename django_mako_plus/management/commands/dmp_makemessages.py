from django.core.management.commands.makemessages import Command as MakeMessagesCommand

from django_mako_plus.util import get_dmp_instance
from django_mako_plus.registry import get_dmp_apps

import os
import os.path


class Command(MakeMessagesCommand):
    help = "Makes messages for Mako templates.  The native makemessages in Django doesn't understand Mako files, so this command compiles all your templates so it can find the compiled .py versions of the templates."


    def add_arguments(self, parser):
        # must call super because not directly subclassing BaseCommand
        super(Command, self).add_arguments(parser)
        # add our additional command
        parser.add_argument('--extra-gettext-option', default=[], dest='extra_gettext_option', action='append', help="Add an additional option to be passed to gettext. Ex: --extra-gettext-option='--keyword=mytrans'")


    def handle(self, *args, **options):
        # go through each dmp_enabled app and compile its mako templates
        for app_config in get_dmp_apps():
            self.compile_mako_files(app_config)

        # add any extra xgettext_options (the regular makemessages doesn't do this, and I need to include other aliases like _(), _z(), etc.
        for opt in options.get('extra_gettext_option', []):
            self.xgettext_options.append(opt)

        # call the superclass command
        return super(Command, self).handle(*args, **options)


    def compile_mako_files(self, app_config):
        '''Compiles the Mako templates within the apps of this system'''
        # go through the files in the templates, scripts, and styles directories
        moddir = os.path.dirname(app_config.module.__file__)
        for subdir_name in ('templates', 'scripts', 'styles'):
            subdir = os.path.join(moddir, subdir_name)
            if os.path.exists(subdir):
                for filename in os.listdir(subdir):
                    fname, ext = os.path.splitext(filename)
                    if ext.lower() in ( '.htm', '.html', '.jsm', '.cssm' ):
                        # create the template object, which creates the compiled .py file
                        renderer = get_dmp_instance().get_template_loader(app_config.name, subdir_name)
                        renderer.get_template(filename)
