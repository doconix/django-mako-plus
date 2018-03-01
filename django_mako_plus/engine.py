from django.apps import apps, AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist
from django.template.backends.base import BaseEngine
from django.utils.module_loading import import_string

from .defaults import DEFAULT_OPTIONS
from .template import MakoTemplateLoader, MakoTemplateAdapter
from .registry import register_dmp_app, ensure_dmp_app, is_dmp_app
from .provider.runner import init_providers
from .util import DMP_INSTANCE_KEY, DMP_OPTIONS

from mako.template import Template

import itertools
import os
import os.path
import re
try:
    # python 3.4+
    pass
except ImportError:
    # python <= 3.4
    pass


# Following Django's lead, hard coding the CSRF processor
_builtin_context_processors = (
    'django_mako_plus.context_processors.csrf',
)

# regex to split the template name in get_template()
# "myapp/mytemplate.html#myblock" gives groups:
# ('myapp', '/mytemplate.html', 'mytemplate.html', '#myblock', 'myblock')
RE_TEMPLATE_NAME = re.compile('([^/?#]*)?(/([^#]*))?(#(.*))?')


#########################################################
###   The main engine


class MakoTemplates(BaseEngine):
    '''
    The primary Mako interface that plugs into the Django templating system.
    This is referenced in settings.py -> TEMPLATES.
    '''
    def __init__(self, params):
        '''Constructor'''
        # start with the default options
        DMP_OPTIONS.update(DEFAULT_OPTIONS)

        # pop the settings.py options into the DMP optionsRUNTIME_TEMPLATE_IMPORTS
        try:
            DMP_OPTIONS.update(params.pop('OPTIONS'))
        except KeyError:
            raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py.  Please ensure the OPTIONS is set in the template setup.')

        # django_mako_plus is always available in templates
        DMP_OPTIONS['RUNTIME_TEMPLATE_IMPORTS'] = [ 'import django_mako_plus' ]
        DMP_OPTIONS['RUNTIME_TEMPLATE_IMPORTS'].extend(DMP_OPTIONS['DEFAULT_TEMPLATE_IMPORTS'])

        # cache our instance in the util module for get_dmp_instance
        # this is a bit of a hack, but it makes calling utility methods possible and efficient
        DMP_OPTIONS[DMP_INSTANCE_KEY] = self
        self.template_loaders = {}

        # super constructor
        super(MakoTemplates, self).__init__(params)

        # set up the context processors
        context_processors = []
        for processor in itertools.chain(_builtin_context_processors, DMP_OPTIONS['CONTEXT_PROCESSORS']):
            context_processors.append(import_string(processor))
        self.template_context_processors = tuple(context_processors)

        # set up the static file providers
        init_providers()

        # add a template renderer for each app in the project directory
        if DMP_OPTIONS['APP_DISCOVERY'] != 'none' and DMP_OPTIONS['APP_DISCOVERY'] is not False:
            for config in apps.get_app_configs():
                if DMP_OPTIONS['APP_DISCOVERY'] == 'all' or os.path.samefile(os.path.dirname(config.path), settings.BASE_DIR):
                    register_dmp_app(config)



    def from_string(self, template_code):
        '''
        Compiles a template from the given string.
        This is one of the required methods of Django template engines.
        '''
        mako_template = Template(template_code, imports=DMP_OPTIONS['RUNTIME_TEMPLATE_IMPORTS'], input_encoding=DMP_OPTIONS['DEFAULT_TEMPLATE_ENCODING'])
        return MakoTemplateAdapter(mako_template)


    def get_template(self, template_name):
        '''
        Retrieves a template object from the pattern "app_name/template.html".
        This is one of the required methods of Django template engines.

        Because DMP templates are always app-specific (Django only searches
        a global set of directories), the template_name MUST be in the format:
        "app_name/template.html" (even on Windows).  DMP splits the template_name
        string on the slash to get the app name and template name.

        Template rendering can be limited to a specific def/block within the template
        by specifying `#def_name`, e.g. `myapp/mytemplate.html#myblockname`.
        '''
        match = RE_TEMPLATE_NAME.match(template_name)
        if match is None or match.group(1) is None or match.group(3) is None:
            raise TemplateDoesNotExist('Invalid template_name format for a DMP template.  This method requires that the template name be in app_name/template.html format (separated by slash).')
        if not is_dmp_app(match.group(1)):
            raise TemplateDoesNotExist('Not a DMP app, so deferring to other template engines for this template')
        return self.get_template_loader(match.group(1)).get_template(match.group(3), def_name=match.group(5))


    def get_template_loader(self, app, subdir='templates', create=False):
        '''
        Returns a template loader object for the given app name in the given subdir.
        For example, get_template_loader('homepage', 'styles') will return
        a loader for the styles/ directory in the homepage app.

        The app parameter can be either an app name or an AppConfig instance.
        The subdir parameter is normally 'templates', 'scripts', or 'styles',
        but it can be any subdirectory name of the given app.

        Normally, you should not have to call this method.  Django automatically
        generates two shortcut functions for every DMP-registered apps,
        and these shortcut functions are the preferred way to render templates.

        This method is useful when you want a custom template loader to a directory
        that does not conform to the app_dir/templates/* pattern.

        If the loader is not found in the DMP cache, one of two things occur:
          1. If create=True, it is created automatically and returned.  This overrides
             the need to register the app as a DMP app.
          2. If create=False, a TemplateDoesNotExist is raised.  This is the default
             behavior.
        '''
        # ensure we have an AppConfig
        if app is None:
            raise TemplateDoesNotExist("Cannot locate loader when app is None")
        if not isinstance(app, AppConfig):
            app = apps.get_app_config(app)

        # get the loader with the path of this app+subdir
        path = os.path.join(app.path, subdir)

        # if create=False, the loader must already exist in the cache
        if not create:
            ensure_dmp_app(app)

        # return the template by path
        return self.get_template_loader_for_path(path, use_cache=True)


    def get_template_loader_for_path(self, path, use_cache=True):
        '''
        Returns a template loader object for the given directory path.
        For example, get_template_loader('/var/mytemplates/') will return
        a loader for that specific directory.

        Normally, you should not have to call this method.  Django automatically
        adds request.dmp.render() and request.dmp.render_to_string() on each
        request.

        This method is useful when you want a custom template loader for a specific
        directory that may be outside your project directory or that is otherwise
        not contained in a normal Django app.  If the directory is inside an app,
        call get_template_loader() instead.

        Unless use_cache=False, this method caches template loaders in the DMP
        cache for later use.
        '''
        # get from the cache if we are able
        if use_cache:
            try:
                return self.template_loaders[path]
            except KeyError:
                pass  # not there, so we'll create

        # create the loader
        loader = MakoTemplateLoader(path, None)

        # cache if we are allowed
        if use_cache:
            self.template_loaders[path] = loader

        # return
        return loader
