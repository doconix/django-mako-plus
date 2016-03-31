from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist, TemplateSyntaxError, Context, RequestContext, engines
from django.template.backends.base import BaseEngine
from django.utils.module_loading import import_string

from mako.exceptions import TopLevelLookupException, TemplateLookupException, CompileException, SyntaxException, html_error_template
from mako.lookup import TemplateLookup
from mako.template import Template

from .exceptions import InternalRedirectException, RedirectException
from .signals import dmp_signal_pre_render_template, dmp_signal_post_render_template, dmp_signal_redirect_exception

from copy import deepcopy
from importlib import import_module
import os, os.path, sys, mimetypes


# set up the logger
import logging
log = logging.getLogger('django_mako_plus')


# a local copy of the options from settings.py
# Django sends when it initializes the MakoTemplates object below.
DMP_OPTIONS = {}


# we cache a few extra things in the options
DMP_OPTIONS_PREFIX = 'django_mako_plus_'
DMP_OPTIONS_INSTANCE_KEY = DMP_OPTIONS_PREFIX + 'instance'


#########################################################
###   The main engine

class MakoTemplates(BaseEngine):
  '''The primary Mako interface that plugs into the Django templating system.
     This is referenced in settings.py -> TEMPLATES.
  '''
  def __init__(self, params):
    '''Constructor'''
    # pop off the options
    params = deepcopy(params)
    try:
      DMP_OPTIONS.update(params.pop('OPTIONS'))
    except KeyError:
      raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py.  Please ensure the OPTIONS is set in the template setup.')

    # super constructor
    super(MakoTemplates, self).__init__(params)

    # set up the context processors
    context_processors = []
    for processor in DMP_OPTIONS.get('CONTEXT_PROESSORS', []):
      context_processors.append(import_string(processor))
    self.template_context_processors = tuple(context_processors)

    # set up the cached instance
    for key in DMP_OPTIONS:
      if key.startswith(DMP_OPTIONS_PREFIX):
        raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py.  Keys starting with "%s" are reserved and cannot be used.' % DMP_OPTIONS_PREFIX)
    DMP_OPTIONS[DMP_OPTIONS_INSTANCE_KEY] = self

    # add a template renderer for each DMP-enabled app
    self.template_lookups = {}
    for app_config in get_dmp_app_configs():
      self.register_app(app_config)


  def register_app(self, app_config):
    '''Registers an app as a "DMP-enabled" app.  Registering creates a cached
       template renderer to make processing faster and adds the dmp_render()
       and dmp_render_to_string() methods to the app.  When Django starts,
       this method is called automatically for any app with
       DJANGO_MAKO_PLUS = True in its __init__.py file.

       This should not normally be called directly.
    '''
    # set up the template, script, and style renderers
    get_app_template_lookup(app_config.name, 'templates', create=True)
    get_app_template_lookup(app_config.name, 'scripts', create=True)
    get_app_template_lookup(app_config.name, 'styles', create=True)

    # add the shortcut functions (only to the main templates, we don't do to scripts or styles
    # because people generally don't call those directly)
    app_config.module.dmp_render = RenderShortcut(self, app_config.name, 'render_to_response')   # the Django shortcut to return an HttpResponse is render().
    app_config.module.dmp_render_to_string = RenderShortcut(self, app_config.name, 'render')  # the Django Template method to render to a string is render().  Django templates never return a direct response.  Lame these two names are the same.


  def get_template_lookup(self, app_name):
    '''Returns the template lookup object for the "templates" directory in
       the given app name from the DMP cache.

       Raises a LookupException if the app_name has not been registered.
    '''
    return self.get_app_template_lookup(app_name, 'templates')


  def get_app_template_lookup(self, app_name, subdir, create=False):
    '''Returns a template lookup object for the given app name in the given subdir.
       For example, get_app_template_lookup('homepage', 'styles') will return
       a lookup for the styles/ directory in the homepage app.

       Normally, you should be calling get_template_lookup() instead of
       this method.  DMP automatically creates template lookup objects for the
       subdirectories 'templates', 'scripts', and 'styles' in every DMP-enabled app.
       Since this is where your templates should normally be placed,
       get_template_lookup() or the shortcuts dmp_render() and
       dmp_render_to_string() should suffice.

       This method is only used when custom lookups are needed.  The app_name
       can be any Django app (regardless of whether it is a DMP-enabled app) OR
       it can be a directory path to any folder on the file path (which should be
       the parent folder of subdir).  In other words, use this method when you
       want to short-circuit the normal DMP caches and normal Django app locations
       and directly make a template lookup to a custom folder.

       If the lookup is not found in the DMP cache, one of two things occur:
         1. If create=True, it is created automatically and returned.  This overrides
            the need to set DJANGO_MAKO_PLUS=True in the app's __init__.py file.
         2. If create=False, a LookupException is raised.  This is the normal
            behavior.
    '''
    # get all the renderers for this app
    try:
      app_lookups = self.template_lookups[app_name]
    except KeyError:
      if create:
        app_lookups = {}
        self.template_lookups[app_name] = app_lookups
      else:
        raise LookupError("%s has not been registered as a DMP app.  Did you forget to include the DJANGO_MAKO_PLUS=True line in your app's __init__.py?" % app_name)

    # get the specific subdir renderer
    try:
      return app_lookups[subdir]
    except KeyError:
      # the template lookup hasn't been cached yet, so create it if create=True
      if create:
        try:
          # if an app name, convert to the app's path
          app_path = apps.get_app_config(app_name).path
        except LookupError:
          # if it wasn't an app name, assume it is an app path
          app_path = os.path.abspath(os.path.join(settings.BASE_DIR, app_name))
        # create the lookup object and return
        lookup = MakoTemplateLookup(app_path, subdir)
        app_lookups[subdir] = lookup
        return lookup
      else:
        # the call opted not to create the lookup, so
        raise LookupError("%s is a DMP app, but a template lookup object for the %s subdirectory was not found." % (app_name, subdir))


  def from_string(self, template_code):
    '''Compiles a template from the given string.
       This is one of the required methods of Django template engines.
    '''
    mako_template = Template(template_code, imports=DMP_OPTIONS.get('DEFAULT_TEMPLATE_IMPORTS'), input_encoding=DMP_OPTIONS.get('DEFAULT_TEMPLATE_ENCODING', 'utf-8'))
    return MakoTemplateAdapter(mako_template)


  def get_template(self, template_name):
    '''Retrieves a template object.
       This is one of the required methods of Django template engines.

       Because DMP templates are always app-specific (Django only searches
       a global set of directories), the template_name MUST be in the format:
       "app_name/template.html".  DMP splits the template_name string on the
       slash to get the app name and template name.
    '''
    parts = template_name.split('/', 1)
    if len(parts) < 2:
      raise LookupError('Invalid template_name format for a DMP template.  This method requires that the template name be in app_name/template.html format (separated by slash).')
    return self.get_template_lookup(parts[0]).get_template(parts[1])






##############################################################
###   Utility functions


def get_dmp_instance():
  '''Retrieves the DMP template engine instance.'''
  # return the instance
  try:
    return DMP_OPTIONS[DMP_OPTIONS_INSTANCE_KEY]
  except KeyError:
    raise ImproperlyConfigured('The Django Mako Plus template engine did not initialize correctly.  Look for previous errors that caused it to fail during initialization.')


def get_dmp_app_configs():
  '''Gets the DMP-enabled app configs, which will be a subset of all installed apps.  This is a generator function.'''
  for config in apps.get_app_configs():
    # check for the DJANGO_MAKO_PLUS = True in the app (should be in app/__init__.py)
    if getattr(config.module, 'DJANGO_MAKO_PLUS', False):
      yield config


def get_template_lookup(app_name):
  '''Returns the template lookup object for the "templates" directory in
     the given app name from the DMP cache.

     Raises a LookupException if the app_name has not been registered.
  '''
  return get_dmp_instance().get_app_template_lookup(app_name, 'templates')


def get_app_template_lookup(app_name, subdir, create=False):
  '''Returns a template lookup object for the given app name in the given subdir.
     For example, get_app_template_lookup('homepage', 'styles') will return
     a lookup for the styles/ directory in the homepage app.

     Normally, you should be calling get_template_lookup() instead of
     this method.  DMP automatically creates template lookup objects for the
     subdirectories 'templates', 'scripts', and 'styles' in every DMP-enabled app.
     Since this is where your templates should normally be placed,
     get_template_lookup() or the shortcuts dmp_render() and
     dmp_render_to_string() should suffice.

     This method is only used when custom lookups are needed.  The app_name
     can be any Django app (regardless of whether it is a DMP-enabled app) OR
     it can be a directory path to any folder on the file path (which should be
     the parent folder of subdir).  In other words, use this method when you
     want to short-circuit the normal DMP caches and normal Django app locations
     and directly make a template lookup to a custom folder.

     If the lookup is not found in the DMP cache, one of two things occur:
       1. If create=True, it is created automatically and returned.  This overrides
          the need to set DJANGO_MAKO_PLUS=True in the app's __init__.py file.
       2. If create=False, a LookupException is raised.  This is the normal
          behavior.
  '''
  return get_dmp_instance().get_app_template_lookup(app_name, subdir, create)



class RenderShortcut(object):
  '''A shortcut way to call render() on a template.
     This enables the primary DMP way to run templates.
     These shortcuts are created in MakoTemplates.__init__ above.
     Use of these shortcuts:

       # this code goes in an app's view files, such as views/index.py
       from .. import render, render_to_string

       # to render templates/index.html to a string
       st = render_to_string(request, 'index.html', { 'var1': 'value' })

       # to render templates/index.html to an HttpResponse
       response = render(request, 'index.html', { 'var1': 'value' })

       # this shows how to render a file in a scripts/ or styles/ folder
       # to render scripts/index.jsm to a string
       st = render_to_string(request, 'index.html', { 'var1': 'value' }, subdir='scripts')

       # to render styles/index.cssm to a response
       response = render(request, 'index.html', { 'var1': 'value' }, subdir='styles')

       # to render a specific "def" block within a template (see Mako documentation for defs)
       response = render(request, 'index.html', { 'var1': 'value' }, def_name='myfunc')
  '''
  def __init__(self, dmp_instance, app_name, template_method_name):
    self.dmp_instance = dmp_instance
    self.app_name = app_name
    self.template_method_name = template_method_name

  def __call__(self, request, template, context=None, def_name=None, subdir='templates'):
    '''Allows instances of this class to act like functions.'''
    # I'm doing "late binding" to the map, just in
    # case new template lookup objects are added after creation.
    # This way I don't have a direct (and permanent) pointer to the lookup object.
    template_lookup = self.dmp_instance.get_app_template_lookup(self.app_name, subdir)
    template_obj = template_lookup.get_template(template)
    return getattr(template_obj, self.template_method_name)(context=context, request=request, def_name=def_name)



##############################################################
###   Looks up Mako templates

class MakoTemplateLookup:
  '''Renders Mako templates.'''
  def __init__(self, app_path, template_subdir='templates'):
    '''Creates a renderer to the given path (relative to the project root where settings.STATIC_ROOT points to).'''
    self.app_path = app_path
    # check the template dir
    template_dir = os.path.abspath(os.path.join(app_path, template_subdir))
    if not os.path.isdir(template_dir):
      raise ImproperlyConfigured('DMP :: Cannot create MakoTemplateRenderer: App %s is missing a required subfolder (it needs %s).' % (app_path, template_subdir))
    # calculate the template search directory
    self.template_search_dirs = [ template_dir ]
    if DMP_OPTIONS.get('TEMPLATES_DIRS'):
      self.template_search_dirs.extend(DMP_OPTIONS.get('TEMPLATES_DIRS'))
    project_path = os.path.normpath(settings.BASE_DIR)
    self.template_search_dirs.append(project_path)
    # calculate the template cache directory
    self.cache_root = os.path.abspath(os.path.join(project_path, app_path, DMP_OPTIONS.get('TEMPLATES_CACHE_DIR', 'templates'), template_subdir))
    self.tlookup = TemplateLookup(directories=self.template_search_dirs, imports=DMP_OPTIONS.get('DEFAULT_TEMPLATE_IMPORTS'), module_directory=self.cache_root, collection_size=2000, filesystem_checks=settings.DEBUG, input_encoding=DMP_OPTIONS.get('DEFAULT_TEMPLATE_ENCODING', 'utf-8'))


  def get_template(self, template):
    '''Retrieve a *Django* template object for the given template name, using the app_path and template_subdir
       settings in this object.

       This method corresponds to the Django templating system API.
       This method raises a Django exception if the template is not found or cannot compile.
    '''
    try:
      # wrap the mako template in an adapter that gives the Django template API
      return MakoTemplateAdapter(self.get_mako_template(template))
    except (TopLevelLookupException, TemplateLookupException) as e: # Mako exception raised
      log.debug('DMP :: template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
      raise TemplateDoesNotExist('Template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
    except (CompileException, SyntaxException) as e: # Mako exception raised
      log.debug('DMP :: template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
      raise TemplateSyntaxError('Template "%s" raised an error: %s' % (template, e))


  def get_mako_template(self, template):
    '''Retrieve a *Mako* template object for the given template name, using the app_path and template_subdir
       settings in this object.

       This method is an alternative to get_template().  Use it when you need the actual Mako template object.
       This method raises a Mako exception if the template is not found or cannot compile.
    '''
    # get the template
    template_obj = self.tlookup.get_template(template)

    # if this is the first time the template has been pulled from self.tlookup, add a few extra attributes
    if not hasattr(template_obj, 'template_path'):
      template_obj.template_path = template
    if not hasattr(template_obj, 'template_full_path'):
      template_obj.template_full_path = template_obj.filename

    # get the template
    return template_obj




class MakoTemplateAdapter(object):
  '''A thin wrapper for a Mako template object that provides the Django API methods.'''
  def __init__(self, mako_template):
    self.mako_template = mako_template


  @property
  def engine(self):
    '''This is a singleton instance because Django only creates one of a given template engine'''
    return get_dmp_instance()


  def render(self, context=None, request=None, def_name=None):
    '''Renders a template using the Mako system.  This method signature conforms to
       the Django template API, which specifies that template.render() returns a string.

       The method triggers two signals:
         1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
            the normal template object that is used for the render operation.
         2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
            template object render.

       @context  A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                 or a Django Context object.
       @request  The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                 file will be ignored but the template will otherwise render fine.
       @def_name Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                 If the section is a <%def>, it must have no parameters.  For example, def_name="foo" will call
                 <%block name="foo"></%block> or <%def name="foo()"></def> within the template.  This is an
                 extension to the Django API, so it is optional.

       The rendered string is returned.
    '''
    # set up the context dictionary, which is the variables available throughout the template
    context_dict = {}
    # let the context_processors add variables to the context.
    if not isinstance(context, Context):
      context = Context(context) if request == None else RequestContext(request, context)
    with context.bind_template(self):
      for d in context:
        context_dict.update(d)

    # send the pre-render signal
    if DMP_OPTIONS.get('SIGNALS', False) and request != None:
      for receiver, ret_template_obj in dmp_signal_pre_render_template.send(sender=self, request=request, context=context, template=self.mako_template):
        if ret_template_obj != None:
          if isinstance(ret_template_obj, MakoTemplateAdapter):
            self.mako_template = ret_template_obj.mako_template   # if the signal function sends a MakoTemplateAdapter back, use the real mako template inside of it
          else:
            self.mako_template = ret_template_obj                 # if something else, we assume it is a mako.template.Template, so use it as the template

    # do we need to limit down to a specific def?
    # this only finds within the exact template (won't go up the inheritance tree)
    # I wish I could make it do so, but can't figure this out
    render_obj = self.mako_template
    if def_name:  # do we need to limit to just a def?
      render_obj = self.mako_template.get_def(def_name)

    # PRIMARY FUNCTION: render the template
    log.debug('DMP :: Rendering template %s' % (self.mako_template.filename or 'string'))
    if settings.DEBUG:
      try:
        content = render_obj.render_unicode(**context_dict)
      except:
        log.exception('DMP :: Exception raised during template rendering:')  # to the console
        content = html_error_template().render_unicode()       # to the browser
    else:  # this is outside the above "try" loop because in non-DEBUG mode, we want to let the exception throw out of here (without having to re-raise it)
      content = render_obj.render_unicode(**context_dict)

    # send the post-render signal
    if DMP_OPTIONS.get('SIGNALS', False) and request != None:
      for receiver, ret_content in dmp_signal_post_render_template.send(sender=self, request=request, context=context, template=self.mako_template, content=content):
        if ret_content != None:
          content = ret_content  # sets it to the last non-None return in the signal receiver chain

    # return
    return content


  def render_to_response(self, context=None, request=None, def_name=None):
    '''Renders the template and returns an HttpRequest object containing its content.

       This method returns a django.http.Http404 exception if the template is not found.
       If the template raises a django_mako_plus.RedirectException, the browser is redirected to
         the given page, and a new request from the browser restarts the entire DMP routing process.
       If the template raises a django_mako_plus.InternalRedirectException, the entire DMP
         routing process is restarted internally (the browser doesn't see the redirect).

       The method triggers two signals:
         1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
            the normal template object that is used for the render operation.
         2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
            template object render.

       @request  The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                 file will be ignored but the template will otherwise render fine.
       @template The template file path to render.  This is relative to the app_path/controller_TEMPLATES_DIR/ directory.
                 For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                 set up the variables as described in the documentation above.
       @context  A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                 or a Django Context object.
       @def_name Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                 If the section is a <%def>, it must have no parameters.  For example, def_name="foo" will call
                 <%block name="foo"></%block> or <%def name="foo()"></def> within the template.
    '''
    try:
      content_type = mimetypes.types_map.get(os.path.splitext(self.mako_template.filename)[1].lower(), 'text/html')
      content = self.render(context=context, request=request, def_name=def_name)
      return HttpResponse(content.encode(settings.DEFAULT_CHARSET), content_type='%s; charset=%s' % (content_type, settings.DEFAULT_CHARSET))
    except RedirectException: # redirect to another page
      e = sys.exc_info()[1]
      if request == None:
        log.debug('DMP :: a template redirected processing to %s' % (request.dmp_router_module, request.dmp_router_function, e.redirect_to))
      else:
        log.debug('DMP :: view function %s.%s redirected processing to %s' % (request.dmp_router_module, request.dmp_router_function, e.redirect_to))
      # send the signal
      if DMP_OPTIONS.get('SIGNALS', False):
        dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
      # send the browser the redirect command
      return e.get_response(request)
