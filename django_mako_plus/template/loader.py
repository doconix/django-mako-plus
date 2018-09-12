from django.apps import apps
from django.conf import settings
from django.template import TemplateDoesNotExist, TemplateSyntaxError

from mako.exceptions import CompileException, SyntaxException, TemplateLookupException, TopLevelLookupException
from mako.lookup import TemplateLookup
from mako.template import Template

from .lexer import DMPLexer
from .adapter import MakoTemplateAdapter

import os
import os.path


class DMPTemplateLookup(TemplateLookup):
    '''Small extension to Mako's template lookup to provide a link back to the MakoTemplateLoader'''
    def __init__(self, template_loader, *args, **kwargs):
        super(DMPTemplateLookup, self).__init__(*args, **kwargs)
        self.template_loader = template_loader


class MakoTemplateLoader(object):
    '''Finds Mako templates for a Django app.'''
    def __init__(self, app_path, template_subdir='templates'):
        '''
        The loader looks in the app_path/templates directory unless
        the template_subdir parameter overrides this default.

        You should not normally create this object because it bypasses
        the DMP cache.  Instead, call get_template_loader() or
        get_template_loader_for_path().
        '''
        self.app_path = app_path
        dmp = apps.get_app_config('django_mako_plus')

        # calculate the template directory and check that it exists
        if template_subdir is None:  # None skips adding the template_subdir
            self.template_dir = os.path.abspath(app_path)
        else:
            self.template_dir = os.path.abspath(os.path.join(app_path, template_subdir))

        # I used to check for the existence of the template dir here, but it caused error
        # checking at engine load time (too soon).  I now wait until get_template() is called,
        # which fails with a TemplateDoesNotExist exception if the template_dir doesn't exist.

        # calculate the cache root and template search directories
        self.cache_root = os.path.join(self.template_dir, dmp.options['TEMPLATES_CACHE_DIR'])
        self.template_search_dirs = [ self.template_dir ]
        self.template_search_dirs.extend(dmp.options['TEMPLATES_DIRS'])
        # Mako doesn't allow parent directory inheritance, such as <%inherit file="../../otherapp/templates/base.html"/>
        # including the project base directory allows this through "absolute" like <%inherit file="/otherapp/templates/base.html"/>
        # (note the leading slash, which means BASE_DIR)
        self.template_search_dirs.append(settings.BASE_DIR)

        # create the actual Mako TemplateLookup, which does the actual work
        self.tlookup = DMPTemplateLookup(
            template_loader=self,
            directories=self.template_search_dirs,
            imports=dmp.template_imports,
            module_directory=self.cache_root,
            collection_size=2000,
            filesystem_checks=settings.DEBUG,
            input_encoding=dmp.options['DEFAULT_TEMPLATE_ENCODING'],
            default_filters=[],  # shouldn't be None because that causes Mako to add an html filter and override DMP's html_filter
            lexer_cls=DMPLexer,
        )


    def get_template(self, template, def_name=None):
        '''Retrieve a *Django* API template object for the given template name, using the app_path and template_subdir
           settings in this object.  This method still uses the corresponding Mako template and engine, but it
           gives a Django API wrapper around it so you can use it the same as any Django template.

           If def_name is provided, template rendering will be limited to the named def/block (see Mako docs).

           This method corresponds to the Django templating system API.
           A Django exception is raised if the template is not found or cannot compile.
        '''
        try:
            # wrap the mako template in an adapter that gives the Django template API
            return MakoTemplateAdapter(self.get_mako_template(template), def_name)
        except (TopLevelLookupException, TemplateLookupException) as e: # Mako exception raised
            raise TemplateDoesNotExist('Template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
        except (CompileException, SyntaxException) as e: # Mako exception raised
            raise TemplateSyntaxError('Template "%s" raised an error: %s' % (template, e))


    def get_mako_template(self, template, force=False):
        '''Retrieve the real *Mako* template object for the given template name without any wrapper,
           using the app_path and template_subdir settings in this object.

           This method is an alternative to get_template().  Use it when you need the actual Mako template object.
           This method raises a Mako exception if the template is not found or cannot compile.

           If force is True, an empty Mako template will be created when the file does not exist.
           This option is used by the providers part of DMP and normally be left False.
        '''
        if template is None:
            raise TemplateLookupException('Template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
        # get the template
        try:
            template_obj = self.tlookup.get_template(template)
        except TemplateLookupException:
            if not force:
                raise
            template_obj = Template('', filename=os.path.join(self.template_dir, template))

        # get the template
        return template_obj
