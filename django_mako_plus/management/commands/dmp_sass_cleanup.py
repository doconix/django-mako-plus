from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django_mako_plus.util import get_dmp_instance, get_dmp_app_configs, DMP_OPTIONS

from optparse import make_option
import os, os.path, shutil, glob




class Command(BaseCommand):
    args = ''
    help = 'Removes orphaned *.css and *.css.map files from your DMP styles/ folders that no longer have companion *.scss files.'
    can_import_settings = True
    option_list = BaseCommand.option_list + (
            make_option(
              '-t',
              '--trial-run',
              action='store_true',
              dest='trial_run',
              default=False,
              help='Display the files that would be removed without actually removing them.'
            ),
            make_option(
              '--verbose',
              action='store_true',
              dest='verbose',
              default=False,
              help='Set verbosity to level 3 (see --verbosity).'
            ),
            make_option(
              '--quiet',
              action='store_true',
              dest='quiet',
              default=False,
              help='Set verbosity to level 0, which silences all messages (see --verbosity).'
            ),
    )# option_list

    def handle(self, *args, **options):
        # save the options for later
        self.options = options
        if self.options['verbose']:
            self.options['verbosity'] = 3
        if self.options['quiet']:
            self.options['verbosity'] = 0
        if self.options['trial_run']:
            self.message("Trial run: dmp_sass_cleanup would have deleted the following files:")

        # ensure we have a base directory
        try:
            if not os.path.isdir(os.path.abspath(settings.BASE_DIR)):
                raise CommandError('Your settings.py BASE_DIR setting is not a valid directory.  Please check your settings.py file for the BASE_DIR variable.')
        except AttributeError as e:
            print(e)
            raise CommandError('Your settings.py file is missing the BASE_DIR setting. Aborting app creation.')

        # go through the DMP apps and check the styles directories
        for config in get_dmp_app_configs():
            styles_dir = os.path.join(config.path, 'styles')
            self.verbose('')
            self.verbose('Checking directory {}:'.format(os.path.relpath(styles_dir, settings.BASE_DIR)))
            self.clean_styles(styles_dir)


    def message(self, msg):
        '''Print a message to the console'''
        if self.options['verbosity'] > 0:
            print(msg)


    def verbose(self, msg):
        '''Print a message based on the verbosity'''
        if self.options['verbosity'] > 1:
            self.message(msg)


    def clean_styles(self, styles_dir):
        '''Removes orphaned .css and .css.map files in the given styles directory.'''
        # go through the files in this directory
        for csspath in glob.glob(os.path.join(styles_dir, '*.css')):
            relcss = os.path.relpath(csspath, settings.BASE_DIR)
            scsspath = '{}.scss'.format(os.path.splitext(csspath)[0])
            mappath = '{}.css.map'.format(os.path.splitext(csspath)[0])

            # if the .scss file exists, it's not orphaned
            if os.path.exists(scsspath):
                self.verbose('Skipping {} because its .scss file still exists.'.format(relcss))
                continue

            # if the css has no sourceMappingURL line, it's not a generated sass file
            smu = '/*# sourceMappingURL={}.map */'.format(os.path.split(csspath)[1])
            if not file_has_line(csspath, smu):
                self.verbose('Skipping {} because it is not a generated Sass file (no "{}").'.format(relcss, smu))
                continue

            # if we get here, the css should be removed
            self.message('Removing {} because it is a generated Sass file, but {} no longer exists.'.format(relcss, os.path.relpath(scsspath, settings.BASE_DIR)))
            if not self.options['trial_run']:
                os.remove(csspath)

            # see if the .css.map file also needs removing
            if os.path.exists(mappath):
                self.message('Removing {} also.'.format(os.path.relpath(mappath, settings.BASE_DIR)))
                if not self.options['trial_run']:
                    os.remove(mappath)




#####################################################
###   Utility functions


def file_has_line(filepath, st):
    '''Returns true if the given file has a line that starts with the given st'''
    with open(filepath) as f:
        for line in f:
            if line.lstrip().startswith(st):
                return True
    return False
