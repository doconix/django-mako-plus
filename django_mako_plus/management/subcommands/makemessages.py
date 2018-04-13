from django.core.management.commands.makemessages import Command as MakeMessagesCommand
from django.template.exceptions import TemplateSyntaxError

from django_mako_plus.registry import get_dmp_apps
from django_mako_plus.convenience import get_template_for_path
from django_mako_plus.management.mixins import DMPCommandMixIn

import os
import os.path


class Command(DMPCommandMixIn, MakeMessagesCommand):
    help = (
        "Makes messages for Mako templates.  The native makemessages in Django doesn't understand "
        "Mako files, so this command compiles all your templates so it can find the compiled .py versions of the templates."
    )

    SEARCH_DIRS = [
        os.path.join('{app_path}', 'templates')
    ]

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--extra-gettext-option',
            default=[],
            dest='extra_gettext_option',
            action='append',
            help="Add an additional option to be passed to gettext. Ex: --extra-gettext-option='--keyword=mytrans'"
        )
        parser.add_argument(
            '--ignore-template-errors',
            action='store_true',
            dest='ignore_template_errors',
            default=False,
            help='Ignore any template errors raised when compiling Mako templates'
        )


    def handle(self, *args, **options):
        self.options = options

        # go through each dmp_enabled app and compile its mako templates
        for app_config in get_dmp_apps():
            self.compile_mako_files(app_config)

        # add any extra xgettext_options (the regular makemessages doesn't do this, and I need to include other aliases like _(), _z(), etc.
        for opt in options.get('extra_gettext_option', []):
           self.xgettext_options.append(opt)

        # call the superclass command
        return MakeMessagesCommand.handle(self, *args, **options)


    def compile_mako_files(self, app_config):
        '''Compiles the Mako templates within the apps of this system'''
        # go through the files in the templates, scripts, and styles directories
        for subdir_name in self.SEARCH_DIRS:
            subdir = subdir_name.format(
                app_path=app_config.path,
                app_name=app_config.name,
            )
            if os.path.exists(subdir):
                for filename in os.listdir(subdir):
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in ( '.htm', '.html', '.mako' ):
                        # create the template object, which creates the compiled .py file
                        filepath = os.path.join(subdir, filename)
                        self.message(filepath, 2)
                        try:
                            get_template_for_path(filepath)
                        except TemplateSyntaxError:
                            if not self.options.get('ignore_template_errors'):
                                raise
