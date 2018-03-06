from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from mako.exceptions import MakoException
from django_mako_plus.registry import get_dmp_apps
from django_mako_plus.provider import create_mako_context
from django_mako_plus.provider.runner import ProviderRun, create_factories
from django_mako_plus.util import get_dmp_instance, split_app, DMP_OPTIONS

import glob
import os, os.path, shutil
import json
from collections import OrderedDict



class Command(BaseCommand):
    args = ''
    help = 'Removes compiled template cache folders in your DMP-enabled app directories.'
    can_import_settings = True


    def add_arguments(self, parser):
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
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrite existing __entry__.js if necessary.'
        )
        parser.add_argument(
            '--single',
            type=str,
            metavar='FILENAME',
            help='Instead of per-app entry files, create a single file that includes the JS for all listed apps.'
        )
        parser.add_argument(
            'appname',
            type=str,
            nargs='*',
            help='The name of one or more DMP apps. If omitted, all DMP apps are processed.'
        )


    def message(self, msg, level=1):
        '''Print a message to the console'''
        # verbosity=1 is the default if not specified in the options
        if self.options['verbosity'] >= level:
            print(msg)


    def handle(self, *args, **options):
        # save the options for later
        self.options = options
        if self.options['verbose']:
            self.options['verbosity'] = 3
        if self.options['quiet']:
            self.options['verbosity'] = 0
        self.factories = create_factories('WEBPACK_PROVIDERS')

        # ensure we have a base directory
        try:
            if not os.path.isdir(os.path.abspath(settings.BASE_DIR)):
                raise CommandError('Your settings.py BASE_DIR setting is not a valid directory.  Please check your settings.py file for the BASE_DIR variable.')
        except AttributeError as e:
            print(e)
            raise CommandError('Your settings.py file is missing the BASE_DIR setting.')

        # main runner for per-app files
        if self.options['single'] is None:
            for config in get_dmp_apps():
                if not options['appname'] or config.name in options['appname']:
                    self.message('Searching `{}` app...'.format(config.name))
                    filename = os.path.join(config.path, 'scripts', '__entry__.js')
                    self.create_entry_file(filename, self.generate_script_map(config))

        # main runner for one sitewide file
        else:
            script_map = {}
            for config in get_dmp_apps():
                if not options['appname'] or config.name in options['appname']:
                    self.message('Searching `{}` app...'.format(config.name))
                    script_map.update(self.generate_script_map(config))
            self.create_entry_file(self.options['single'], script_map)


    def generate_script_map(self, config):
        '''
        Maps templates in this app to their scripts.  This function iterates through
        app/templates/* to find the templates in this app.  Returns the following
        dictionary:

        {
            'app/template1': [ './scripts/template1.js', './scripts/supertemplate1.js' ],
            'app/template2': [ './scripts/template2.js', './scripts/supertemplate2.js', './scripts/supersuper2.js' ],
            ...
        }

        Any files or subdirectories starting with double-underscores (e.g. __dmpcache__) are skipped.
        '''
        script_map = OrderedDict()
        template_root = os.path.join(config.path, 'templates')
        def recurse(folder):
            for filename in os.listdir(os.path.join(template_root, folder)):
                if filename.startswith('__'):
                    continue
                filerel = os.path.join(folder, filename)
                filepath = os.path.join(os.path.join(template_root, filerel))
                if os.path.isdir(filepath):
                    recurse(filerel)

                elif os.path.isfile(filepath):
                    scripts = self.template_scripts(config, filerel)
                    key = '{}/{}'.format(config.name, os.path.splitext(filerel)[0])
                    if len(scripts) > 0:
                        script_map[key] = scripts
                        self.message('\t{}: {}'.format(key, scripts), 3)
                    else:
                        self.message('\t{}: none found'.format(key), 3)

        recurse('')
        return script_map


    def template_scripts(self, config, template_name):
        '''
        Returns a list of scripts used by the given template object AND its ancestors.

        This runs a ProviderRun on the given template (as if it were being displayed).
        This allows the WEBPACK_PROVIDERS to provide the JS files to us.

        For this algorithm to work, providers must populate the provider data dictionary like this example.
        the built-in JsLinkProvider does this already.
            column_data = {
                'urls': [
                    '/static/app/scripts/first.js',
                    '/static/app/scripts/second.js',
                    ...
                ]
            }
        '''
        template_obj = get_dmp_instance().get_template_loader(config, create=True).get_mako_template(template_name, force=True)
        mako_context = create_mako_context(template_obj)
        inner_run = ProviderRun(mako_context['self'], factories=self.factories)
        inner_run.run()
        scripts = []
        for data in inner_run.column_data:
            for url in data.get('urls', []):
                url = url.split('?', 1)[0]
                scripts.append(os.path.relpath(url, settings.BASE_DIR))
        return scripts


    def create_entry_file(self, filename, script_map):
        '''Creates an entry file for the given script map'''
        if len(script_map) == 0:
            return
        if not self.options['overwrite'] and os.path.exists(filename):
            raise ValueError('Refusing to destroy existing file: {} (use --overwrite option or remove the file)'.format(filename))
        self.message('Creating {}'.format(os.path.relpath(filename, settings.BASE_DIR)))
        with open(filename, 'w') as fout:
            fout.write('(context => {\n')
            filedir = os.path.dirname(filename)
            for page, scripts in script_map.items():
                fout.write('    DMP_CONTEXT.appBundles["%s"] = () => { %s; };\n' % (
                    page,
                    '; '.join([ 'require("./%s")' % os.path.relpath(s, filedir) for s in scripts ]),
                ))
            fout.write('})(DMP_CONTEXT.get());\n')
