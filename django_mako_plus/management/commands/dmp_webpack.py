from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from django_mako_plus import LinkProvider
from django_mako_plus.template import create_mako_context
from django_mako_plus.provider.runner import ProviderRun
from django_mako_plus.management.mixins import DMPCommandMixIn
from mako.template import Template as MakoTemplate
import os
import os.path
from collections import OrderedDict



class Command(DMPCommandMixIn, BaseCommand):
    help = 'Removes compiled template cache folders in your DMP-enabled app directories.'
    can_import_settings = True

    def __init__(self, *args, running_inline=False, **kwargs):
        # special option when called from providers/webpack.py
        self.running_inline = running_inline
        super().__init__(*args, **kwargs)


    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrite existing __entry__.js if it exists'
        )
        parser.add_argument(
            '--single',
            type=str,
            metavar='FILENAME',
            help='Instead of per-app entry files, create a single file that includes the JS for all listed apps'
        )
        parser.add_argument(
            'appname',
            type=str,
            nargs='*',
            help='The name of one or more DMP apps. If omitted, all DMP apps are processed'
        )


    def handle(self, *args, **options):
        dmp = apps.get_app_config('django_mako_plus')
        self.options = options
        WebpackProviderRun.initialize_providers()
        for pci in WebpackProviderRun.CONTENT_PROVIDERS:
            if not issubclass(pci.cls, LinkProvider):
                raise ImproperlyConfigured('Invalid provider {} listed in {}: must extend django_mako_plus.LinkProvider'.format(pci.cls.__qualname__, WebpackProviderRun.SETTINGS_KEY))

        # ensure we have a base directory
        try:
            if not os.path.isdir(os.path.abspath(settings.BASE_DIR)):
                raise CommandError('Your settings.py BASE_DIR setting is not a valid directory.  Please check your settings.py file for the BASE_DIR variable.')
        except AttributeError:
            raise CommandError('Your settings.py file is missing the BASE_DIR setting.')

        # the apps to process
        enapps = []
        for appname in options.get('appname'):
            enapps.append(apps.get_app_config(appname))
        if len(enapps) == 0:
            enapps = dmp.get_registered_apps()

        # main runner for per-app files
        created = False
        if options.get('single') is None:
            for app in enapps:
                self.message('Searching `{}` app...'.format(app.name), level=3)
                filename = os.path.join(app.path, 'scripts', '__entry__.js')
                created = self.create_entry_file(filename, self.generate_script_map(app), [ app ]) or created

        # main runner for one sitewide file
        else:
            script_map = {}
            for app in enapps:
                self.message('Searching `{}` app...'.format(app.name), level=3)
                script_map.update(self.generate_script_map(app))
            created = self.create_entry_file(options.get('single'), script_map, enapps) or created


    def create_entry_file(self, filename, script_map, enapps):
        '''Creates an entry file for the given script map'''
        if len(script_map) == 0:
            return

        # create the entry file
        template = MakoTemplate('''
<%! import os %>
// dynamic imports are within functions so they don't happen until called
DMP_CONTEXT.loadBundle({
    %for (app, template), script_paths in script_map.items():

    "${ app }/${ template }": () => [
        %for path in script_paths:
        import(/* webpackMode: "eager" */ "./${ os.path.relpath(path, os.path.dirname(filename)) }"),
        %endfor
    ],
    %endfor

})
''')
        content = template.render(
            enapps=enapps,
            script_map=script_map,
            filename=filename,
        ).strip()

        # ensure the parent directories exist
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        # if the file exists, then consider the options
        file_exists = os.path.exists(filename)
        if file_exists and self.running_inline:
            # running inline means that we're in debug mode and webpack is likely watching, so
            # we don't want to recreate the entry file (and cause webpack to constantly reload)
            # unless we have changes
            with open(filename, 'r') as fin:
                if content == fin.read():
                    return False
        if file_exists and not self.options.get('overwrite'):
            raise CommandError('Refusing to destroy existing file: {} (use --overwrite option or remove the file)'.format(filename))

        # if we get here, write the file
        self.message('Creating {}'.format(os.path.relpath(filename, settings.BASE_DIR)), level=3)
        with open(filename, 'w') as fout:
            fout.write(content)
        return True

    def generate_script_map(self, config):
        '''
        Maps templates in this app to their scripts.  This function deep searches
        app/templates/* for the templates of this app.  Returns the following
        dictionary with absolute paths:

        {
            ( 'appname', 'template1' ): [ '/abs/path/to/scripts/template1.js', '/abs/path/to/scripts/supertemplate1.js' ],
            ( 'appname', 'template2' ): [ '/abs/path/to/scripts/template2.js', '/abs/path/to/scripts/supertemplate2.js', '/abs/path/to/scripts/supersuper2.js' ],
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
                        key = ( config.name, os.path.splitext(template_name)[0] )
                        self.message('Found template: {}; static files: {}'.format(key, scripts), level=3)
                        script_map[key] = scripts

            for subdir in subdirs:
                recurse(subdir)

        recurse(template_root)
        return script_map


    def template_scripts(self, config, template_name):
        '''
        Returns a list of scripts used by the given template object AND its ancestors.

        This runs a ProviderRun on the given template (as if it were being displayed).
        This allows the WEBPACK_PROVIDERS to provide the JS files to us.
        '''
        dmp = apps.get_app_config('django_mako_plus')
        template_obj = dmp.engine.get_template_loader(config, create=True).get_mako_template(template_name, force=True)
        mako_context = create_mako_context(template_obj)
        inner_run = WebpackProviderRun(mako_context['self'])
        inner_run.run()
        scripts = []
        for tpl in inner_run.templates:
            for p in tpl.providers:
                if os.path.exists(p.absfilepath):
                    scripts.append(p.absfilepath)
        return scripts



###############################################################################
###   Specialized provider run for the above management command

class WebpackProviderRun(ProviderRun):
    SETTINGS_KEY = 'WEBPACK_PROVIDERS'

    def _get_template_inheritance(self):
        '''
        Normally, this returns a list of the template inheritance of tself, starting with the oldest ancestor.
        But for the webpack one, we just want the template itself, without any ancestors.
        This gives the static files for this exact template (not including all ancestors).
        '''
        return [ self.tself.template ]
