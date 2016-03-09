from django.apps import apps
from django.conf import settings
from django.template.backends.base import BaseEngine
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist, TemplateSyntaxError, Context, RequestContext

from mako.exceptions import TopLevelLookupException, html_error_template
from mako.lookup import TemplateLookup

from .exceptions import InternalRedirectException, RedirectException

import os, os.path, sys, mimetypes
from copy import deepcopy



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
    try:
      # pop off the options
      params = deepcopy(params)
      try:
        DMP_OPTIONS.update(params.pop('OPTIONS'))
      except KeyError:
        raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py.  Please ensure the OPTIONS is set in the template setup.')
        
      # set up the cached instance
      for key in DMP_OPTIONS:
        if key.startswith(DMP_OPTIONS_PREFIX):
          raise ImproperlyConfigured('The Django Mako Plus template OPTIONS were not set up correctly in settings.py.  Keys starting with "%s" are reserved and cannot be used.' % DMP_OPTIONS_PREFIX)
      DMP_OPTIONS[DMP_OPTIONS_INSTANCE_KEY] = self

      # super constructor
      super(MakoTemplates, self).__init__(params)

      # add a template renderer for each DMP-enabled app
      self.template_renderers = {}
      for app_config in get_dmp_app_configs():
        self.register_app(app_config)
        
    except Exception as e:
      import traceback
      traceback.print_exc()

    
  def register_app(self, app_config):
    '''Registers an app as a "DMP-enabled" app.  Registering creates a cached
       template renderer to make processing faster and adds the dmp_render()
       and dmp_render_to_string() methods to the app.  When Django starts,
       this method is called automatically for any app with 
       DJANGO_MAKO_PLUS = True in its __init__.py file.
       
       This should not normally be called directly.
    '''
    # set up the template, script, and style renderers
    self.template_renderers[app_config.name] = {
      'templates': MakoTemplateRenderer(app_config.path),
      'scripts': MakoTemplateRenderer(app_config.path, 'scripts'),
      'styles': MakoTemplateRenderer(app_config.path, 'styles'),
    }

    # add the shortcut functions (only to the main templates, we don't do to scripts or styles
    # because people generally don't call those directly)
    app_config.module.dmp_render = RenderShortcut(self, app_config.name, 'render', 'templates')
    app_config.module.dmp_render_to_string = RenderShortcut(self, app_config.name, 'render_to_string', 'templates')
    
    
  @property
  def template_context_processors(self):
    '''Returns the template context processors that are set in the options'''
    return DMP_OPTIONS.get(
    
    
  def get_renderer(self, app_name):
    '''Returns the template renderer for the given app name from the cache.
       Raises a LookupException if the app_name has not been registered.
       
       This is the primary interface for getting an MakoTemplateRenderer.
    '''
    return self._get_renderer(app_name, 'templates')


  def _get_renderer(self, app_name, renderer_type):
    '''Returns the styles renderer for the given app name from the cache.
       Raises a LookupException if the app_name has not been registered.
       
       This method is generally only used internally within DMP.
       
       renderer_type is one of 'templates', 'scripts', or 'styles'.
    '''
    try:
      return self.template_renderers[app_name][renderer_type]
    except KeyError:
      raise LookupError("%s has not been registered as a DMP app (or the renderer_type was invalid).  Did you forget to include the DJANGO_MAKO_PLUS = True line in your app's __init__.py?" % app_name)

  
  def from_string(self, template_code):
    '''Compiles a template from the given string.  
       This is one of the required methods of Django template engines.
    '''
    return ''


  def get_template(self, template_name):
    '''Retrieves a template.
       This is one of the required methods of Django template engines.
    '''
    return ''
    
    
    



##############################################################
###   Utilities not meant to be used outside this package.


def get_dmp_instance():
  '''Retrieves the DMP template engine instance.'''
  return DMP_OPTIONS[DMP_OPTIONS_INSTANCE_KEY]


def get_dmp_app_configs():
  '''Gets the DMP-enabled app configs, which will be a subset of all installed apps.  This is a generator function.'''
  for config in apps.get_app_configs():
    # check for the DJANGO_MAKO_PLUS = True in the app (should be in app/__init__.py)
    if getattr(config.module, 'DJANGO_MAKO_PLUS', False):
      yield config
      

class RenderShortcut(object):
  '''A shortcut way to call render() for an app's template renderer.
     The code in this class is a bit convoluted, but it makes it possible
     to call each app's renderer with a function rather than having to get
     an object reference.
  '''
  def __init__(self, dmp_instance, app_name, method_name, renderer_type):
    self.dmp_instance = dmp_instance
    self.app_name = app_name
    self.method_name = method_name
    self.renderer_type = renderer_type

  def __call__(self, *args, **kwargs):
    '''Allows instances of this class to act like functions.'''
    # I use get_renderer to essentially do "late binding" to the map, just in
    # case the TEMPLATE_RENDERERS map must be modified after its initial creation
    # below.  This way I don't have a direct (and permanent) pointer to the renderer.
    # this next line gets the appropriate MakoTemplateRenderer and calls the render or
    # render_to_string method.
    return getattr(self.dmp_instance._get_renderer(self.app_name, self.renderer_type), self.method_name)(*args, **kwargs)



##############################################################
###   Renders Mako templates

class MakoTemplateRenderer:
  '''Renders Mako templates.'''
  def __init__(self, app_path, template_subdir='templates'):
    '''Creates a renderer to the given path (relative to the project root where settings.STATIC_ROOT points to).'''
    self.app_path = app_path
    # check the template dir
    template_dir = os.path.abspath(os.path.join(app_path, template_subdir))
    if not os.path.isdir(template_dir):
      raise ImproperlyConfigured('DMP :: Cannot create MakoTemplateRenderer: App %s has no templates folder (it needs %s).' % (app_name, template_dir))
    # calculate the template search directory
    self.template_search_dirs = [ template_dir ]
    if DMP_OPTIONS.get('TEMPLATES_DIRS'):
      self.template_search_dirs.extend(DMP_OPTIONS.get('TEMPLATES_DIRS'))
    project_path = os.path.normpath(settings.BASE_DIR)
    self.template_search_dirs.append(project_path)
    # calculate the template cache directory
    self.cache_root = os.path.abspath(os.path.join(project_path, app_path, DMP_OPTIONS.get('TEMPLATES_CACHE_DIR', 'templates'), template_subdir))
    self.tlookup = TemplateLookup(directories=self.template_search_dirs, imports=DMP_OPTIONS.get('DEFAULT_TEMPLATE_IMPORTS'), module_directory=self.cache_root, collection_size=2000, filesystem_checks=settings.DEBUG, input_encoding=DMP_OPTIONS.get('DEFAULT_TEMPLATE_ENCODING', 'utf-8'))


  @property
  def engine(self):
    '''This is a singleton instance because Django only creates one of a given template engine'''
    return get_dmp_instance()


  def get_template(self, template):
    '''Retrieve a template object for the given template name, using the app_path and template_subdir
       settings in this object.
    '''
    template_obj = self.tlookup.get_template(template)
    # if this is the first time the template has been pulled from self.tlookup, add a few extra attributes
    if not hasattr(template_obj, 'template_path'):
      template_obj.template_path = template
    if not hasattr(template_obj, 'template_full_path'):
      template_obj.template_full_path = template_obj.filename
    if not hasattr(template_obj, 'mako_template_renderer'):
      template_obj.mako_template_renderer = self
    return template_obj


  def render_to_string(self, request, template, params={}, def_name=None):
    '''Runs a template and returns a string.  Normally, you probably want to call render() instead
       because it gives a full HttpResponse or Http404.

       This method raises a mako.exceptions.TopLevelLookupException if the template is not found.

       The method throws two signals:
         1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
            the normal template object that is used for the render operation.
         2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
            template object render.

       @request  The request context from Django.  If this is None, 1) any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                 file will be ignored and 2) DMP signals will not be sent, but the template will otherwise render fine.
       @template The template file path to render.  This is relative to the app_path/controller_TEMPLATES_DIR/ directory.
                 For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                 set up the variables as described in the documentation above.
       @params   A dictionary of name=value variables to send to the template page.
       @def_name Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                 If the section is a <%def>, it must have no parameters.  For example, def_name="foo" will call
                 <%block name="foo"></%block> or <%def name="foo()"></def> within the template.
                 The block/def must be defined in the exact template.  DMP does not support calling defs from
                 super-templates.
    '''
    # must convert the request context to a real dict to use the ** below
    context_dict = {}
    context_dict['request'] = request
    context_dict['settings'] = settings
    try:
      context_dict['STATIC_URL'] = settings.STATIC_URL  # this is used so much in templates, it's useful to have it always available
    except AttributeError:
      pass
    # create the context (the parameters).  Django has some built-in Context Processors that can be run.
    context = Context(params) if request == None else RequestContext(request, params)  
    with context.bind_template(self):
      for d in context:
        context_dict.update(d)

    # get the template
    template_obj = self.get_template(template)

    # send the pre-render signal
    if DMP_OPTIONS.get('SIGNALS', False) and request != None:
      for receiver, ret_template_obj in signals.dmp_signal_pre_render_template.send(sender=self, request=request, context=context, template=template_obj):
        if ret_template_obj != None:  # changes the template object to the received
          template_obj = ret_template_obj

    # do we need to limit down to a specific def?
    # this only finds within the exact template (won't go up the inheritance tree)
    # I wish I could make it do so, but can't figure this out
    render_obj = template_obj
    if def_name:  # do we need to limit to just a def?
      render_obj = template_obj.get_def(def_name)

    # PRIMARY FUNCTION: render the template
    log.debug('DMP :: rendering template %s' % template_obj.filename)
    if settings.DEBUG:
      try:
        content = render_obj.render_unicode(**context_dict)
      except:
        content = html_error_template().render_unicode()
    else:  # this is outside the above "try" loop because in non-DEBUG mode, we want to let the exception throw out of here (without having to re-raise it)
      content = render_obj.render_unicode(**context_dict)

    # send the post-render signal
    if DMP_OPTIONS.get('SIGNALS', False) and request != None:
      for receiver, ret_content in signals.dmp_signal_post_render_template.send(sender=self, request=request, context=context, template=template_obj, content=content):
        if ret_content != None:
          content = ret_content  # sets it to the last non-None return in the signal receiver chain

    # return
    return content


  def render(self, request, template, params={}, def_name=None):
    '''Runs a template and returns an HttpRequest object to it.

       This method returns a django.http.Http404 exception if the template is not found.
       If the template raises a django_mako_plus.RedirectException, the browser is redirected to
         the given page, and a new request from the browser restarts the entire DMP routing process.
       If the template raises a django_mako_plus.InternalRedirectException, the entire DMP
         routing process is restarted internally (the browser doesn't see the redirect).

       The method throws two signals:
         1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
            the normal template object that is used for the render operation.
         2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
            template object render.

       @request  The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                 file will be ignored but the template will otherwise render fine.
       @template The template file path to render.  This is relative to the app_path/controller_TEMPLATES_DIR/ directory.
                 For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                 set up the variables as described in the documentation above.
       @params   A dictionary of name=value variables to send to the template page.
       @def_name Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                 If the section is a <%def>, it must have no parameters.  For example, def_name="foo" will call
                 <%block name="foo"></%block> or <%def name="foo()"></def> within the template.
    '''
    try:
      content_type = mimetypes.types_map.get(os.path.splitext(template)[1].lower(), 'text/html')
      content = self.render_to_string(request, template, params, def_name)
      return HttpResponse(content.encode(settings.DEFAULT_CHARSET), content_type='%s; charset=%s' % (content_type, settings.DEFAULT_CHARSET))
    except TopLevelLookupException: # template file not found
      log.debug('DMP :: template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
      raise Http404()
    except RedirectException: # redirect to another page
      e = sys.exc_info()[1] # Py2.7 and Py3+ compliant
      log.debug('DMP :: view function %s.%s redirected processing to %s' % (request.dmp_router_module, request.dmp_router_function, e.redirect_to))
      # send the signal
      if DMP_OPTIONS.get('SIGNALS', False):
        signals.dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
      # send the browser the redirect command
      return e.get_response(request)


