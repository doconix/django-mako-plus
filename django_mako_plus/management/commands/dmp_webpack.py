from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django_mako_plus.util import DMP_OPTIONS, get_dmp_app_configs

from django_mako_plus.provider import create_mako_context
from django_mako_plus.provider.runner import ProviderRun, create_factories
from django_mako_plus.util import get_dmp_instance, split_app

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
            'appname',
            type=str,
            nargs='*',
            help='The name of an app. If omitted, __entry__.js files are created in all DMP apps.'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrite existing __entry__.js if necessary.'
        )



    def handle(self, *args, **options):
        # save the options for later
        self.options = options
        if self.options['verbose']:
            self.options['verbosity'] = 3
        if self.options['quiet']:
            self.options['verbosity'] = 0

        # ensure we have a base directory
        try:
            if not os.path.isdir(os.path.abspath(settings.BASE_DIR)):
                raise CommandError('Your settings.py BASE_DIR setting is not a valid directory.  Please check your settings.py file for the BASE_DIR variable.')
        except AttributeError as e:
            print(e)
            raise CommandError('Your settings.py file is missing the BASE_DIR setting.')

        # run for each dmp-enabled app
        self.factories = create_factories('WEBPACK_PROVIDERS')
        for config in get_dmp_app_configs():
            if not options['appname'] or config.name in options['appname']:
                self.create_entry(config)


    def message(self, msg, level=1):
        '''Print a message to the console'''
        # verbosity=1 is the default if not specified in the options
        if self.options['verbosity'] >= level:
            print(msg)


    def create_entry(self, config):
        '''Creates a webpack __entry__.js file in the given app'''
        templates_dir = os.path.join(config.path, 'templates')
        entry_filename = os.path.join(config.path, 'scripts', '__entry__.js')
        # map templates to their scripts
        page_map = OrderedDict()
        for template_name in os.listdir(templates_dir):
            if os.path.isfile(os.path.join(os.path.join(templates_dir, template_name))):
                template_obj = get_dmp_instance().get_template_loader(config, create=True).get_mako_template(template_name)
                pages = self.template_scripts(template_obj)
                page_map.update(pages)
        # write the file
        if not self.options['overwrite'] and os.path.exists(entry_filename):
            raise ValueError('Refusing to destroy existing file: %s.  Use --overwrite option or remove the file.' % (entry_filename,))
        if len(page_map) == 0:
            self.message('Templates in app {} had no matching scripts'.format(config.name))
        else:
            self.message('Templates in app {} required {} script(s); creating {}'.format(config.name, len(page_map), os.path.relpath(entry_filename, settings.BASE_DIR)))
            with open(entry_filename, 'w') as fout:
                fout.write('(context => {\n')
                for page, scripts in page_map.items():
                    fout.write('    DMP_CONTEXT.appBundles["%s"] = () => { %s; };\n' % (
                        page,
                        '; '.join([ 'require("%s")' % (s,) for s in scripts ]),
                    ))
                fout.write('})(DMP_CONTEXT.get());\n')


    def template_scripts(self, template_obj):
        '''Maps the scripts used by the given template and its ancestors'''
        # for this algorithm to work, providers must populate the provider data dictionary like this example.
        # the built-in JsLinkProvider does this already.
        # provider_data = {
        #     'urls': [
        #         '/static/app/scripts/first.js',
        #         '/static/app/scripts/second.js',
        #         ...
        #     ]
        # }
        mako_context = create_mako_context(template_obj)
        inner_run = ProviderRun(mako_context['self'], factories=self.factories)
        inner_run.get_content()
        pages = {}
        for data in inner_run.provider_data:
            # determine the app and template
            app_config, template_path = split_app(template_obj.filename)
            _, filename = template_path.split('/', 1)
            page, _ = os.path.splitext(filename)
            # determine the relative location of the urls
            scripts_dir = os.path.join(app_config.name, 'scripts')
            scripts = []
            for url in data.get('urls', []):
                url = url.split('?')[0]
                scripts.append(os.path.join('.', os.path.relpath(url, scripts_dir)))
            if len(scripts) > 0:
                pages['{}/{}'.format(app_config.name, page)] = scripts
        return pages





