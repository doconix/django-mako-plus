from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django_mako_plus.template import create_mako_context
from django_mako_plus.provider.runner import ProviderRun, init_provider_factories
from django_mako_plus.management.mixins import DMPCommandMixIn

import sys
import os
import os.path
from collections import OrderedDict
from datetime import datetime


class Command(DMPCommandMixIn, BaseCommand):
    help = 'Removes compiled template cache folders in your DMP-enabled app directories.'
    can_import_settings = True


    def add_arguments(self, parser):
        super().add_arguments(parser)

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


    def handle(self, *args, **options):
        dmp = django_apps.get_app_config('django_mako_plus')
        self.options = options
        self.factories = init_provider_factories('WEBPACK_PROVIDERS')

        # ensure we have a base directory
        try:
            if not os.path.isdir(os.path.abspath(settings.BASE_DIR)):
                raise CommandError('Your settings.py BASE_DIR setting is not a valid directory.  Please check your settings.py file for the BASE_DIR variable.')
        except AttributeError as e:
            raise CommandError('Your settings.py file is missing the BASE_DIR setting.')

        # the apps to process
        apps = []
        for appname in options.get('appname'):
            apps.append(django_apps.get_app_config(appname))
        if len(apps) == 0:
            apps = dmp.get_registered_apps()

        # main runner for per-app files
        if options.get('single') is None:
            for app in apps:
                self.message('Searching `{}` app...'.format(app.name))
                filename = os.path.join(app.path, 'scripts', '__entry__.js')
                self.create_entry_file(filename, self.generate_script_map(app), [ app ])

        # main runner for one sitewide file
        else:
            script_map = {}
            for app in apps:
                self.message('Searching `{}` app...'.format(app.name))
                script_map.update(self.generate_script_map(app))
            self.create_entry_file(options.get('single'), script_map, apps)


    def create_entry_file(self, filename, script_map, apps):
        '''Creates an entry file for the given script map'''
        def in_apps(s):
            for app in apps:
                last = None
                path = os.path.dirname(s)
                while last != path:
                    if os.path.samefile(app.path, path):
                        return True
                    last = path
                    path = os.path.dirname(last)
            return False

        filedir = os.path.dirname(filename)
        if os.path.exists(filename):
            if self.options.get('overwrite'):
                os.remove(filename)
            else:
                raise CommandError('Refusing to destroy existing file: {} (use --overwrite option or remove the file)'.format(filename))

        # create the lines of the entry file
        lines = []
        for page, scripts in script_map.items():
            require = []
            for script_path in scripts:
                if in_apps(script_path):
                    require.append('require("./{}")'.format(os.path.relpath(script_path, filedir)))
            if len(require) > 0:
                lines.append('DMP_CONTEXT.appBundles["{}"] = () => {{ \n        {};\n    }};'.format(page, ';\n        '.join(require)))

        # if we had at least one line, write the entry file
        if len(lines) > 0:
            self.message('Creating {}'.format(os.path.relpath(filename, settings.BASE_DIR)))
            with open(filename, 'w') as fout:
                fout.write('// Generated on {} by `{}`\n'.format(
                    datetime.now().strftime('%Y-%m-%d %H:%M'),
                    ' '.join(sys.argv),
                ))
                fout.write('// Contains links for app{}: {}\n'.format(
                    's' if len(apps) > 1 else '',
                    ', '.join(sorted([ app.name for app in apps ])),
                ))
                fout.write('\n')
                fout.write('(context => {\n')
                for line in lines:
                    fout.write('    {}\n'.format(line))
                fout.write('})(DMP_CONTEXT.get());\n')


    def generate_script_map(self, config):
        '''
        Maps templates in this app to their scripts.  This function iterates through
        app/templates/* to find the templates in this app.  Returns the following
        dictionary with paths relative to BASE_DIR:

        {
            'app/template1': [ '/abs/path/to/scripts/template1.js', '/abs/path/to/scripts/supertemplate1.js' ],
            'app/template2': [ '/abs/path/to/scripts/template2.js', '/abs/path/to/scripts/supertemplate2.js', '/abs/path/to/scripts/supersuper2.js' ],
            ...
        }

        Any files or subdirectories starting with double-underscores (e.g. __dmpcache__) are skipped.
        '''
        script_map = OrderedDict()
        template_root = os.path.join(os.path.relpath(config.path, settings.BASE_DIR), 'templates')
        def recurse(folder):
            subdirs = []
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    if filename.startswith('__'):
                        continue
                    filerel = os.path.join(folder, filename)
                    if os.path.isdir(filerel):
                        subdirs.append(filerel)

                    elif os.path.isfile(filerel):
                        template_name = os.path.relpath(filerel, template_root)
                        scripts = self.template_scripts(config, template_name)
                        key = '{}/{}'.format(config.name, os.path.splitext(template_name)[0])
                        if len(scripts) > 0:
                            script_map[key] = scripts
                            self.message('\t{}: {}'.format(key, scripts), 3)
                        else:
                            self.message('\t{}: none found'.format(key), 3)
            for subdir in subdirs:
                recurse(subdir)

        recurse(template_root)
        return script_map


    def template_scripts(self, config, template_name):
        '''
        Returns a list of scripts used by the given template object AND its ancestors.

        This runs a ProviderRun on the given template (as if it were being displayed).
        This allows the WEBPACK_PROVIDERS to provide the JS files to us.

        For this algorithm to work, the providers must extend static_links.LinkProvider
        because that class creates the 'enabled' list of provider instances, and each
        provider instance has a url.
        '''
        dmp = django_apps.get_app_config('django_mako_plus')
        template_obj = dmp.engine.get_template_loader(config, create=True).get_mako_template(template_name, force=True)
        mako_context = create_mako_context(template_obj)
        inner_run = ProviderRun(mako_context['self'], factories=self.factories)
        inner_run.run()
        scripts = []
        for data in inner_run.column_data:
            for provider in data.get('enabled', []):    # if file doesn't exist, the provider won't be enabled
                if hasattr(provider, 'filepath'):       # providers used to collect for webpack must have a .filepath property
                    scripts.append(provider.filepath)   # the absolute path to the file (see providers/static_links.py)
        return scripts
