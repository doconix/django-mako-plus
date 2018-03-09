from django.core.management.commands.makemessages import Command as MakeMessagesCommand

from django_mako_plus.registry import get_dmp_apps
from django_mako_plus.convenience import get_template_for_path

import os
import os.path


class Command(MakeMessagesCommand):
    help = "Makes messages for Mako templates.  The native makemessages in Django doesn't understand Mako files, so this command compiles all your templates so it can find the compiled .py versions of the templates."
    SEARCH_DIRS = [
        os.path.join('{app_path}', 'templates')
    ]

    def message(self, msg, level=1):
        '''Print a message to the console'''
        # verbosity=1 is the default if not specified in the options
        if self.options['verbosity'] >= level:
            print(msg)


    def add_arguments(self, parser):
        # must call super because not directly subclassing BaseCommand
        super(Command, self).add_arguments(parser)
        # add our additional command
        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='Set verbosity to level 3 (see --verbosity).'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Set verbosity to level 0, which silences all messages (see --verbosity).'
        )
        parser.add_argument(
            '--extra-gettext-option',
            default=[],
            dest='extra_gettext_option',
            action='append',
            help="Add an additional option to be passed to gettext. Ex: --extra-gettext-option='--keyword=mytrans'"
        )


    def handle(self, *args, **options):
        self.options = options
        if self.options['verbose']:
            self.options['verbosity'] = 3
        if self.options['quiet']:
            self.options['verbosity'] = 0

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
                        get_template_for_path(filepath)
