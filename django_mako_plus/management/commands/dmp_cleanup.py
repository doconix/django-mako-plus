from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django_mako_plus.util import DMP_OPTIONS
from django_mako_plus.registry import get_dmp_apps

import os, os.path, shutil




class Command(BaseCommand):
    args = ''
    help = 'Removes compiled template cache folders in your DMP-enabled app directories.'
    can_import_settings = True


    def add_arguments(self, parser):
        parser.add_argument(
            '--trial-run',
            action='store_true',
            dest='trial_run',
            default=False,
            help='Display the folders that would be removed without actually removing them.'
        )
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


    def handle(self, *args, **options):
        # save the options for later
        self.options = options
        if self.options['verbose']:
            self.options['verbosity'] = 3
        if self.options['quiet']:
            self.options['verbosity'] = 0
        if self.options['trial_run']:
            self.message("Trial run: dmp_cleanup would have deleted the following folders:", level=1)

        # ensure we have a base directory
        try:
            if not os.path.isdir(os.path.abspath(settings.BASE_DIR)):
                raise CommandError('Your settings.py BASE_DIR setting is not a valid directory.  Please check your settings.py file for the BASE_DIR variable.')
        except AttributeError as e:
            print(e)
            raise CommandError('Your settings.py file is missing the BASE_DIR setting.')

        # check each dmp-enabled app
        for config in get_dmp_apps():
            self.message('Cleaning up app: {}'.format(config.name), level=1)
            for subdir in ( 'templates', 'scripts', 'styles' ):
                cache_dir = os.path.join(config.path, subdir, DMP_OPTIONS['TEMPLATES_CACHE_DIR'])
                if os.path.exists(cache_dir):
                    self.message('Removing {}'.format(pretty_relpath(cache_dir, settings.BASE_DIR)), level=2)
                    if not self.options['trial_run']:
                        shutil.rmtree(cache_dir)
                else:
                    self.message('Skipping {} because it does not exist'.format(pretty_relpath(cache_dir, settings.BASE_DIR)), level=2)


    def message(self, msg, level):
        '''Print a message to the console'''
        # verbosity=1 is the default if not specified in the options
        if self.options['verbosity'] >= level:
            print(msg)





#####################################################
###   Utility functions



def pretty_relpath(path, start):
    '''
    Returns a relative path, but only if it doesn't start with a non-pretty parent directory ".."
    '''
    relpath = os.path.relpath(path, start)
    if relpath.startswith('..'):
        return path
    return relpath
