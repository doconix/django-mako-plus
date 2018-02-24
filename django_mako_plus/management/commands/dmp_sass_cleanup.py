from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django_mako_plus.registry import get_dmp_apps

import glob
import os
import os.path




class Command(BaseCommand):
    args = ''
    help = 'Removes orphaned *.css, *.css.map, *.cssm, and *.cssm.map files from your DMP styles/ folders that no longer have companion *.scss files.'
    can_import_settings = True


    def add_arguments(self, parser):
        parser.add_argument(
            '--trial-run',
            action='store_true',
            dest='trial_run',
            default=False,
            help='Display the files that would be removed without actually removing them.'
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
        parser.add_argument(
            '--directory',
            action='store',
            dest='directory',
            default='',
            help='Check the given directory instead of searching through DMP app styles/ folders.'
        )
        parser.add_argument(
            '--recursive',
            action='store_true',
            dest='recursive',
            default=False,
            help="Recurse to subdirectories in each search folder.  This option searches subdirectories of each app's styles/ folder, or when specified with --directory, searches subdirectories of the given directory."
        )


    def handle(self, *args, **options):
        # save the options for later
        self.options = options
        if self.options['verbose']:
            self.options['verbosity'] = 3
        if self.options['quiet']:
            self.options['verbosity'] = 0
        if self.options['trial_run']:
            self.message("Trial run: dmp_sass_cleanup would have deleted the following files:", level=1)

        # ensure we have a base directory
        try:
            if not os.path.isdir(os.path.abspath(settings.BASE_DIR)):
                raise CommandError('Your settings.py BASE_DIR setting is not a valid directory.  Please check your settings.py file for the BASE_DIR variable.')
        except AttributeError as e:
            print(e)
            raise CommandError('Your settings.py file is missing the BASE_DIR setting.')

        # create a list of directories to check (default to each app's styles/)
        styles_directories = [ os.path.join(config.path, 'styles') for config in get_dmp_apps() ]
        if self.options['directory']:
            if not os.path.isdir(self.options['directory']):
                raise CommandError('The specified directory does not exist: {}'.format(self.options['directory']))
            styles_directories = [ self.options['directory'] ]

        # if we are in recursive mode, add all subdirectories of the search folders
        if self.options['recursive']:
            styles_directories = [ d[0] for styles_dir in styles_directories for d in os.walk(styles_dir) ]

        # check the directories
        for styles_dir in styles_directories:
            self.message('Checking directory {}'.format(pretty_relpath(styles_dir, settings.BASE_DIR)), level=2)
            self.clean_styles(styles_dir)


    def message(self, msg, level):
        '''Print a message to the console'''
        # verbosity=1 is the default if not specified in the options
        if self.options['verbosity'] >= level:
            print(msg)


    def clean_styles(self, styles_dir):
        '''Removes orphaned .css and .css.map files in the given styles directory.'''
        # go through the files in this directory
        for ext in ( 'css', 'cssm' ):
            for csspath in glob.glob(os.path.join(styles_dir, '*.{}'.format(ext))):
                relcss = pretty_relpath(csspath, settings.BASE_DIR)
                scsspath = '{}.s{}'.format(os.path.splitext(csspath)[0], ext)
                mappath = '{}.{}.map'.format(os.path.splitext(csspath)[0], ext)

                # if the .scss file exists, it's not orphaned
                if os.path.exists(scsspath):
                    self.message('Skipping {} because its .scss file still exists.'.format(relcss), level=3)
                    continue

                # if the css has no sourceMappingURL line, it's not a generated sass file
                smu = '/*# sourceMappingURL={}.map */'.format(os.path.split(csspath)[1])
                if not file_has_line(csspath, smu):
                    self.message('Skipping {} because it is not a generated Sass file (no "{}").'.format(relcss, smu), level=3)
                    continue

                # if we get here, the css should be removed
                self.message('Removing {} because it is a generated Sass file, but {} no longer exists.'.format(relcss, pretty_relpath(scsspath, settings.BASE_DIR)), level=1)
                if not self.options['trial_run']:
                    os.remove(csspath)

                # see if the .css.map file also needs removing
                if os.path.exists(mappath):
                    self.message('Removing {} also.'.format(pretty_relpath(mappath, settings.BASE_DIR)), level=1)
                    if not self.options['trial_run']:
                        os.remove(mappath)




#####################################################
###   Utility functions


def file_has_line(filepath, st):
    '''
    Returns true if the given file has a line that starts with the given st
    '''
    with open(filepath) as f:
        for line in f:
            if line.lstrip().startswith(st):
                return True
    return False


def pretty_relpath(path, start):
    '''
    Returns a relative path, but only if it doesn't start with a non-pretty parent directory ".."
    '''
    relpath = os.path.relpath(path, start)
    if relpath.startswith('..'):
        return path
    return relpath
