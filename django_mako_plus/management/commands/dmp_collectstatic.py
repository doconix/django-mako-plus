from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django_mako_plus.util import get_dmp_instance, get_dmp_app_configs, DMP_OPTIONS

from optparse import make_option
import os, os.path, shutil, fnmatch
from importlib import import_module


# import minification if requested
JSMIN = False
CSSMIN = False
if DMP_OPTIONS.get('MINIFY_JS_CSS', False):
    try:
        from rjsmin import jsmin
        JSMIN = True
    except ImportError:
        raise CommandError('The Django Mako Plus option "MINIFY_JS_CSS" is True in settings.py, but the "rjsmin" module does not seem to be installed. Do you need to "pip install" it?')
    try:
        from rcssmin import cssmin
        CSSMIN = True
    except ImportError:
        raise CommandError('The Django Mako Plus option "MINIFY_JS_CSS" is True in settings.py, but the "rcssmin" module does not seem to be installed. Do you need to "pip install" it?')



class Command(BaseCommand):
    args = ''
    help = 'Collects static files, such as media, scripts, and styles, to a common directory root. This is done to prepare for deployment.'
    can_import_settings = True
    
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrite existing files in the directory when necessary.'
        )
        parser.add_argument(
            '--ignore',
            action='append',
            dest='ignore_files',
            help='Ignore the given file/directory.  Unix-style wildcards are acceptable, such as "*.txt".  This option can be specified more than once.'
        )


    def handle(self, *args, **options):
        # save the options for later
        self.options = options

        # ensure we have a base directory
        try:
            if not os.path.isdir(os.path.abspath(settings.BASE_DIR)):
                raise CommandError('Your settings.py BASE_DIR setting is not a valid directory.  Please check your settings.py file for the BASE_DIR variable.')
        except AttributeError as e:
            print(e)
            raise CommandError('Your settings.py file is missing the BASE_DIR setting. Aborting app creation.')

        # get the destination directory, and ensure it doesn't already exist
        # if dest_root starts with a /, it is an absolute directory
        # if dest_root doesn't start with a /, it goes relative to the BASE_DIR
        try:
            dest_root = os.path.join(os.path.abspath(settings.BASE_DIR), settings.STATIC_ROOT)
            if os.path.exists(dest_root) and not self.options['overwrite']:
                raise CommandError('The destination directory for static files (%s) already exists. Please delete it or run this command with the --overwrite option.' % dest_root)
        except AttributeError:
            raise CommandError('Your settings.py file is missing the STATIC_ROOT setting. Exiting without collecting the static files.')

        # create the directory - we assume it either doesn't exist, or the --overwrite is specified
        if not os.path.isdir(dest_root):
            os.makedirs(dest_root)

        # go through the DMP apps and collect the static files
        for config in get_dmp_app_configs():
            self.copy_dir(config.path, os.path.abspath(os.path.join(dest_root, config.name)))



    def ignore_file(self, fname):
        '''Returns whether the given filename should be ignored, based on the --ignore options sent into the command'''
        if self.options['ignore_files']:
            for pattern in self.options['ignore_files']:
                if fnmatch.fnmatch(fname, pattern):
                    return True
        return False


    def copy_dir(self, source, dest, level=0):
        '''Copies the static files from one directory to another.  If this command is run, we assume the user wants to overwrite any existing files.'''
        # ensure the destination exists
        if not os.path.exists(dest):
            os.mkdir(dest)
        # go through the files in this directory
        for fname in os.listdir(source):
            source_path = os.path.join(source, fname)
            dest_path = os.path.join(dest, fname)
            ext = os.path.splitext(fname)[1].lower()

            ###  EXPLICIT IGNORE  ###
            if self.ignore_file(fname):
                pass

            ###  DIRECTORIES  ###
            # ignore these directories
            elif os.path.isdir(source_path) and fname in ( 'migrations', 'templates', 'views', DMP_OPTIONS.get('TEMPLATES_CACHE_DIR'), '__pycache__' ):
                pass

            # if a directory, create it in the destination and recurse
            elif os.path.isdir(source_path):
                if not os.path.exists(dest_path):
                    os.mkdir(dest_path)
                elif not os.path.isdir(dest_path):  # could be a file or link
                    os.unlink(dest_path)
                    os.mkdir(dest_path)
                self.copy_dir(source_path, dest_path, level+1)

            ###   FILES   ###
            # we don't do any regular files at the top level
            elif level == 0:
                pass

            # ignore these files
            elif fname in ( '__init__.py', ):
                pass

            # ignore these extensions
            elif ext in ( '.cssm', '.jsm' ):
                pass

            # if a regular Javscript file, minify it
            elif ext == '.js' and DMP_OPTIONS.get('MINIFY_JS_CSS', False) and JSMIN:
                with open(source_path) as fin:
                    with open(dest_path, 'w') as fout:
                        fout.write(jsmin(fin.read()))

            elif ext == '.css' and DMP_OPTIONS.get('MINIFY_JS_CSS', False) and CSSMIN:
                with open(source_path) as fin:
                    with open(dest_path, 'w') as fout:
                        fout.write(cssmin(fin.read()))

            # if we get here, it's a binary file like an image, movie, pdf, etc.
            else:
                shutil.copy2(source_path, dest_path)
