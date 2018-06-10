from django.apps import apps
from django.core.management.base import CommandError
from django.contrib.staticfiles.management.commands.collectstatic import Command as CollectStaticCommand
from django.conf import settings
from django_mako_plus.management.mixins import DMPCommandMixIn

import os, os.path, shutil, fnmatch

try:
    from rjsmin import jsmin
except ImportError:
    jsmin = None
try:
    from rcssmin import cssmin
except ImportError:
    cssmin = None



TYPE_DIRECTORY = 0       # file is a directory
TYPE_FILE = 1            # file is a regular file


class Rule(object):
    def __init__(self, pattern, level, filetype, score):
        self.pattern = pattern
        self.level = level
        self.filetype = filetype
        self.score = score

    def match(self, fname, flevel, ftype):
        '''Returns the result score if the file matches this rule'''
        # if filetype is the same
        # and level isn't set or level is the same
        # and pattern matche the filename
        if self.filetype == ftype and (self.level is None or self.level == flevel) and fnmatch.fnmatch(fname, self.pattern):
            return self.score
        return 0





class Command(DMPCommandMixIn, CollectStaticCommand):
    help = 'Collects static files, such as media, scripts, and styles, to a common directory root. This is done to prepare for deployment.'
    can_import_settings = True

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrite existing files in the directory when necessary.'
        )
        parser.add_argument(
            '--no-minify',
            action='store_true',
            dest='no_minify',
            help='Do not minify *.css with rcssmin and *.js with rjsmin.',
        )
        parser.add_argument(
            '--include-dir',
            action='append',
            dest='include_dir',
            help='Include directories matching this pattern.  Unix-style wildcards are acceptable, such as "*partial*".  This option can be specified more than once.'
        )
        parser.add_argument(
            '--include-file',
            action='append',
            dest='include_file',
            help='Include files matching this pattern.  Unix-style wildcards are acceptable, such as "*.txt".  This option can be specified more than once.'
        )
        parser.add_argument(
            '--skip-dir',
            action='append',
            dest='skip_dir',
            help='Skip directories matching this pattern.  Unix-style wildcards are acceptable, such as "*partial*".  This option can be specified more than once.'
        )
        parser.add_argument(
            '--skip-file',
            action='append',
            dest='skip_file',
            help='Skip files matching this pattern.  Unix-style wildcards are acceptable, such as "*.txt".  This option can be specified more than once.'
        )


    def handle(self, *args, **options):
        dmp = apps.get_app_config('django_mako_plus')
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
            if os.path.exists(dest_root) and not self.options.get('overwrite'):
                raise CommandError('The destination directory for static files (%s) already exists. Please delete it or run this command with the --overwrite option.' % dest_root)
        except AttributeError:
            raise CommandError('Your settings.py file is missing the STATIC_ROOT setting. Exiting without collecting the static files.')

        # create the directory - we assume it either doesn't exist, or the --overwrite is specified
        if not os.path.isdir(dest_root):
            os.makedirs(dest_root)

        # set up the rules
        self.rules = self.create_rules()

        # go through the DMP apps and collect the static files
        for config in dmp.get_registered_apps():
            self.message('Processing app {}'.format(config.name), 1)
            self.copy_dir(config.path, os.path.abspath(os.path.join(dest_root, config.name)))


    def create_rules(self):
        '''Adds rules for the command line options'''
        dmp = apps.get_app_config('django_mako_plus')
        # the default
        rules = [
            # files are included by default
            Rule('*',                                    level=None, filetype=TYPE_FILE,      score=1),
            # files at the app level are skipped
            Rule('*',                                    level=0,    filetype=TYPE_FILE,      score=-2),
            # directories are recursed by default
            Rule('*',                                    level=None, filetype=TYPE_DIRECTORY, score=1),
            # directories at the app level are skipped
            Rule('*',                                    level=0,    filetype=TYPE_DIRECTORY, score=-2),

            # media, scripts, styles directories are what we want to copy
            Rule('media',                                level=0,    filetype=TYPE_DIRECTORY, score=6),
            Rule('scripts',                              level=0,    filetype=TYPE_DIRECTORY, score=6),
            Rule('styles',                               level=0,    filetype=TYPE_DIRECTORY, score=6),

            # ignore the template cache directories
            Rule(dmp.options['TEMPLATES_CACHE_DIR'],     level=None, filetype=TYPE_DIRECTORY, score=-3),
            # ignore python cache directories
            Rule('__pycache__',                          level=None, filetype=TYPE_DIRECTORY, score=-3),
            # ignore compiled python files
            Rule('*.pyc',                                level=None, filetype=TYPE_FILE,      score=-3),
        ]
        # include rules have score of 50 because they trump all initial rules
        for pattern in (self.options.get('include_dir') or []):
            self.message('Setting rule - recurse directories: {}'.format(pattern), 1)
            rules.append(Rule(pattern, level=None, filetype=TYPE_DIRECTORY, score=50))
        for pattern in (self.options.get('include_file') or []):
            self.message('Setting rule - include files: {}'.format(pattern), 1)
            rules.append(Rule(pattern, level=None, filetype=TYPE_FILE, score=50))
        # skip rules have score of 100 because they trump everything, including the includes from the command line
        for pattern in (self.options.get('skip_dir') or []):
            self.message('Setting rule - skip directories: {}'.format(pattern), 1)
            rules.append(Rule(pattern, level=None, filetype=TYPE_DIRECTORY, score=-100))
        for pattern in (self.options.get('skip_file') or []):
            self.message('Setting rule - skip files: {}'.format(pattern), 1)
            rules.append(Rule(pattern, level=None, filetype=TYPE_FILE, score=-100))
        return rules


    def copy_dir(self, source, dest, level=0):
        '''Copies the static files from one directory to another.  If this command is run, we assume the user wants to overwrite any existing files.'''
        encoding = settings.DEFAULT_CHARSET or 'utf8'
        msglevel = 2 if level == 0 else 3
        self.message('Directory: {}'.format(source), msglevel, level)

        # create a directory for this app
        if not os.path.exists(dest):
            self.message('Creating directory: {}'.format(dest), msglevel, level+1)
            os.mkdir(dest)

        # go through the files in this app
        for fname in os.listdir(source):
            source_path = os.path.join(source, fname)
            dest_path = os.path.join(dest, fname)
            ext = os.path.splitext(fname)[1].lower()

            # get the score for this file
            score = 0
            for rule in self.rules:
                score += rule.match(fname, level, TYPE_DIRECTORY if os.path.isdir(source_path) else TYPE_FILE)

            # if score is not above zero, we skip this file
            if score <= 0:
                self.message('Skipping file with score {}: {}'.format(score, source_path), msglevel, level+1)
                continue

            ### if we get here, we need to copy the file ###

            # if a directory, recurse to it
            if os.path.isdir(source_path):
                self.message('Creating directory with score {}: {}'.format(score, source_path), msglevel, level+1)
                # create it in the destination and recurse
                if not os.path.exists(dest_path):
                    os.mkdir(dest_path)
                elif not os.path.isdir(dest_path):  # could be a file or link
                    os.unlink(dest_path)
                    os.mkdir(dest_path)
                self.copy_dir(source_path, dest_path, level+1)

            # if a regular Javscript file, run through the static file processors (scripts group)
            elif ext == '.js' and not self.options.get('no_minify') and jsmin:
                self.message('Including and minifying file with score {}: {}'.format(score, source_path), msglevel, level+1)
                with open(source_path, encoding=encoding) as fin:
                    with open(dest_path, 'w', encoding=encoding) as fout:
                        minified = minify(fin.read(), jsmin)
                        fout.write(minified)


            # if a CSS file, run through the static file processors (styles group)
            elif ext == '.css' and not self.options.get('no_minify') and cssmin:
                self.message('Including and minifying file with score {}: {}'.format(score, source_path), msglevel, level+1)
                with open(source_path, encoding=encoding) as fin:
                    with open(dest_path, 'w', encoding=encoding) as fout:
                        minified = minify(fin.read(), cssmin)
                        fout.write(minified)

            # otherwise, just copy the file
            else:
                self.message('Including file with score {}: {}'.format(score, source_path), msglevel, level+1)
                shutil.copy2(source_path, dest_path)



##############################################
###   Utility functions

def minify(text, minifier):
    '''Minifies the source text (if needed)'''
    # there really isn't a good way to know if a file is already minified.
    # our heuristic is if source is more than 50 bytes greater of dest OR
    # if a hard return is found in the first 50 chars, we assume it is not minified.
    minified = minifier(text)
    if  abs(len(text) - len(minified)) > 50 or '\n' in text[:50]:
        return minified
    return text
