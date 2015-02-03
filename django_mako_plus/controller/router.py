#!/usr/bin/env python3

from django.apps import AppConfig
from django.core.urlresolvers import get_mod_func
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, StreamingHttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.conf import settings
from django.template import Context, RequestContext
from django.utils.importlib import import_module
from mako.exceptions import TopLevelLookupException, html_error_template
from mako.lookup import TemplateLookup
from ..controller import signals, view_function, RedirectException, InternalRedirectException
import os, os.path, re, mimetypes, sys
try:
  from urllib.parse import unquote_plus  # Py3+
except ImportError:
  from urllib import unquote_plus        # Py2.7


# set up the logger
import logging 
log = logging.getLogger('django_mako_plus')




##############################################################
###   The front controller of all views on the site.
###   urls.py routes everything through this method.

def route_request(request):
    '''The main router for all calls coming in to the system.'''
    # output the variables so the programmer can debug where this is routing
    log.debug('DMP :: processing: app=%s, page=%s, func=%s, urlparams=%s' % (request.dmp_router_app, request.dmp_router_page, request.dmp_router_function, request.urlparams))

    # set the full function location
    request.dmp_router_module = '.'.join([ request.dmp_router_app, 'views', request.dmp_router_page ])
    
    # first try going to the view function for this request
    # we look for a views/name.py file where name is the same name as the HTML file
    response = None
    
    while True: # enables the InternalRedirectExceptions to loop around
      full_module_filename = os.path.normpath(os.path.join(settings.BASE_DIR, request.dmp_router_module.replace('.', '/') + '.py'))
      try:
        # look for the module, and if not found go straight to template
        if not os.path.exists(full_module_filename):
          log.debug('DMP :: module %s not found; sending processing directly to template %s.html' % (request.dmp_router_module, request.dmp_router_page_full))
          try:
            dmp_renderer = get_renderer(request.dmp_router_app)
          except ImproperlyConfigured as e: 
            log.debug('DMP :: %s' % (e))
            raise Http404
          return dmp_renderer.render_to_response(request, '%s.html' % request.dmp_router_page_full)
        
        # find the function
        module_obj = import_module(request.dmp_router_module)
        if not hasattr(module_obj, request.dmp_router_function):
          log.debug('DMP :: view function %s not in module %s; returning 404 not found.' % (request.dmp_router_function, request.dmp_router_module))
          raise Http404
        func_obj = getattr(module_obj, request.dmp_router_function)

        # ensure it is decorated with @view_function - this is for security so only certain functions can be called
        if not isinstance(func_obj, view_function): 
          log.debug('DMP :: view function %s found successfully, but it is not decorated with "view_function"; returning 404 not found.' % (request.dmp_router_function))
          raise Http404

        # send the pre-signal
        if settings.DMP_SIGNALS:
          for receiver, ret_response in signals.dmp_signal_pre_process_request.send(sender=sys.modules[__name__], request=request):
            if isinstance(ret_response, (HttpResponse, StreamingHttpResponse)):
              return ret_response

        # call view function
        log.debug('DMP :: calling view function %s.%s' % (request.dmp_router_module, request.dmp_router_function))
        response = getattr(module_obj, request.dmp_router_function)(request)
              
        # send the post-signal
        if settings.DMP_SIGNALS:
          for receiver, ret_response in signals.dmp_signal_post_process_request.send(sender=sys.modules[__name__], request=request, response=response):
            if ret_response != None:
              response = ret_response # sets it to the last non-None in the signal receiver chain
            
        # if we didn't get a correct response back, send a 404
        if not isinstance(response, (HttpResponse, StreamingHttpResponse)):
          log.debug('DMP :: view function %s.%s failed to return an HttpResponse (or the post-signal overwrote it).  Returning Http404.' % (request.dmp_router_module, request.dmp_router_function))
          raise Http404
              
        # return the response
        return response
        
      except InternalRedirectException:
        ivr = sys.exc_info()[1] # Py2.7 and Py3+ compliant
        # send the signal
        if settings.DMP_SIGNALS:
          signals.dmp_signal_internal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=ivr)
        # do the internal redirect
        request.dmp_router_module = ivr.redirect_module
        request.dmp_router_function = ivr.redirect_function
        full_module_filename = os.path.normpath(os.path.join(settings.BASE_DIR, request.dmp_router_module.replace('.', '/') + '.py'))
        log.debug('DMP :: received an InternalViewRedirect to %s -> %s' % (full_module_filename, request.dmp_router_function))
      
      except RedirectException: # redirect to another page
        e = sys.exc_info()[1] # Py2.7 and Py3+ compliant
        log.debug('DMP :: view function %s.%s redirected processing to %s' % (request.dmp_router_module, request.dmp_router_function, e.redirect_to))
        # send the signal
        if settings.DMP_SIGNALS:
          signals.dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
        # send the browser the redirect command
        return e.get_response(request)

    # the code should never get here
    raise Exception("Django-Mako-Plus router error: The route_request() function should not have been able to get to this point.  Please notify the owner of the DMP project.  Thanks.")
    


##############################################################
###   Renders Mako templates

class MakoTemplateRenderer:
  '''Renders Mako templates.'''
  def __init__(self, app_path, template_subdir='templates'):
    '''Creates a renderer to the given path (relateive to the project root where settings.STATIC_ROOT points to)'''
    project_path = os.path.normpath(settings.BASE_DIR)
    self.app_path = app_path
    template_dir = get_app_template_dir(app_path, template_subdir)  # raises ImproperlyConfigured if error
    self.template_search_dirs = [ template_dir ]
    if settings.DMP_TEMPLATES_DIRS:
      self.template_search_dirs.extend(settings.DMP_TEMPLATES_DIRS)
    self.template_search_dirs.append(settings.BASE_DIR)
    self.cache_root = os.path.abspath(os.path.join(project_path, app_path, settings.DMP_TEMPLATES_CACHE_DIR, template_subdir)) 
    self.tlookup = TemplateLookup(directories=self.template_search_dirs, imports=settings.DMP_DEFAULT_TEMPLATE_IMPORTS, module_directory=self.cache_root, collection_size=2000, filesystem_checks=settings.DEBUG)


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


  def render(self, request, template, params={}, def_name=None):
    '''Runs a template and returns a string.  Normally, you probably want to call render_to_response instead
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
    context_dict = { 'request': request, 'settings': settings }  # this allows the template to access the request
    context = Context(params) if request == None else RequestContext(request, params)  # Django's RequestContext automatically runs all the TEMPLATE_CONTEXT_PROCESSORS and populates with variables
    for d in context:
      context_dict.update(d)

    # get the template 
    template_obj = self.get_template(template)

    # send the pre-render signal
    if settings.DMP_SIGNALS and request != None:
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
    if settings.DMP_SIGNALS and request != None:
      for receiver, ret_content in signals.dmp_signal_post_render_template.send(sender=self, request=request, context=context, template=template_obj, content=content):
        if ret_content != None:
          content = ret_content  # sets it to the last non-None return in the signal receiver chain
          
    # return
    return content
    
    
  def render_to_response(self, request, template, params={}, def_name=None):
    '''Runs a template and returns an HttpRequest object to it. 
    
       This method returns a django.http.Http404 exception if the template is not found.
       If the template raises a django_mako_plus.controller.RedirectException, the browser is redirected to
         the given page, and a new request from the browser restarts the entire DMP routing process.
       If the template raises a django_mako_plus.controller.InternalRedirectException, the entire DMP
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
      content = self.render(request, template, params, def_name)
      return HttpResponse(content.encode(settings.DEFAULT_CHARSET), content_type='%s; charset=%s' % (content_type, settings.DEFAULT_CHARSET))
    except TopLevelLookupException: # template file not found    
      log.debug('DMP :: template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
      raise Http404()
    except RedirectException: # redirect to another page
      e = sys.exc_info()[1] # Py2.7 and Py3+ compliant
      log.debug('DMP :: view function %s.%s redirected processing to %s' % (request.dmp_router_module, request.dmp_router_function, e.redirect_to))
      # send the signal
      if settings.DMP_SIGNALS:
        signals.dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
      # send the browser the redirect command
      return e.get_response(request)





################################################################
###   get_renderer - provides easy access to singleton
###   templates, one per app


# a cache of template renderers for the apps
# this is populated by DMPAppConfig at the bottom
# of this file.
TEMPLATE_RENDERERS = {}


def get_renderer(app_name):
  '''Retrieves the renderer for the given app.  DMP creates a new
     renderer object for each DMP-enabled app in your project.
     This renderer object keeps track of the app's template directory
     as well as a cached lookup of template objects for speed.
     
     This renderer object is available in two ways:
       1. Primarily, through the myapp.dmp_renderer object; see the tutorial for more information.
       2. Secondarily, through this method: django_mako_plus.controller.router.get_renderer('myapp').
     
     If the app_name is not a valid DMP app or is not listed in
     settings.INSTALLED_APPS, and ImproperlyConfigured exception 
     is raised.
  '''
  try:
    return TEMPLATE_RENDERERS[app_name]
  except KeyError:
    raise ImproperlyConfigured('App %s is not a designated DMP app.  Template rendering is not possible without DJANGO_MAKO_PLUS=True in its __init__.py file.' % (app_name))






##########################################################
###   Middleware the prepares the request for
###   use with the controller. 

class RequestInitMiddleware:
  '''Adds several fields to the request that our controller needs.
  
     This class MUST be included in settings.py -> MIDDLEWARE_CLASSES.
  '''
  
  def process_request(self, request):
    '''Called for each browser request.  This adds the following fields to the request object:
    
       request.dmp_router_app       The Django application (such as "calculator").
       request.dmp_router_page      The view module (such as "calc" for calc.py).
       request.dmp_router_page_full The view module as specified in the URL, including the function name if specified.
       request.dmp_router_function  The function within the view module to be called (usually "process_request").
       request.dmp_router_module    The module path in Python terms, such as calculator.views.calc.
       request.urlparams            A list of the remaining url parts (see the calc.py example).
       
       This method is run as part of the middleware processing, so it runs long
       before the route_request() method at the top of this file.
    '''
    # split the path
    path_parts = request.path[1:].split('/') # [1:] to remove the leading /
      
    # ensure that we have at least 2 path_parts to work with
    # by adding the default app and/or page as needed
    if len(path_parts) == 0:
      path_parts.append(settings.DMP_DEFAULT_APP)
      path_parts.append(settings.DMP_DEFAULT_PAGE)
      
    elif len(path_parts) == 1: # /app or /page
      if path_parts[0] in TEMPLATE_RENDERERS:  # one of our apps specified, so insert the default page
        path_parts.append(settings.DMP_DEFAULT_PAGE)
      else:  # not one of our apps, so insert the app and assume path_parts[0] is a page in that app
        path_parts.insert(0, settings.DMP_DEFAULT_APP)
        if not path_parts[1]: # was the page empty?
          path_parts[1] = settings.DMP_DEFAULT_PAGE
    
    else: # at this point in the elif, we know len(path_parts) >= 2
      if path_parts[0] not in TEMPLATE_RENDERERS: # the first part was not one of our apps, so insert the default app
        path_parts.insert(0, settings.DMP_DEFAULT_APP)
      if not path_parts[1]:  # is the page empty?
        path_parts[1] = settings.DMP_DEFAULT_PAGE
        
    # set the app and page in the request
    request.dmp_router_app = path_parts[0]
    request.dmp_router_page = path_parts[1]
    request.dmp_router_page_full = path_parts[1]  # might be different from dmp_router_page when split by '.' below
    
    # see if a function is specified with the page (the . separates a function name)
    du_pos = request.dmp_router_page.find('.')
    if du_pos >= 0:
      request.dmp_router_function = request.dmp_router_page[du_pos+1:]
      request.dmp_router_page = request.dmp_router_page[:du_pos]
    else:
      du_pos = request.dmp_router_page.find('__')  # __ can also separate the function name, this is a deprecated way to do it - we'll support it for the near future
      if du_pos >= 0:
        request.dmp_router_function = request.dmp_router_page[du_pos+2:]
        request.dmp_router_page = request.dmp_router_page[:du_pos]
      else:  # the . not found, and the __ not found, so go to default function name
        request.dmp_router_function = 'process_request'

    # set up the urlparams with the reamining path parts
    request.urlparams = URLParamList([ unquote_plus(s) for s in path_parts[2:] ])
    
        


class URLParamList(list):  
  '''A simple extension to Python's list that returns '' for indices that don't exist.  
     For example, if the object is ['a', 'b'] and you call obj[5], it will return '' 
     rather than throwing an IndexError.  This makes dealing with url parameters 
     simpler since you don't have to check the length of the list.'''
  def __getitem__(self, idx):
    '''Returns the element at idx, or '' if idx is beyond the length of the list'''
    # if the index is beyond the length of the list, return ''
    if isinstance(idx, int) and (idx >= len(self) or idx < -1 * len(self)):
      return ''
    # else do the regular list function (for int, splice types, etc.)
    return list.__getitem__(self, idx)
  



  
################################################################################
###   Initialize the template renderers and performs other setup for DMP


# Note that I don't use apps.get_app_configs() here because ths code can be called before other
# apps are set up (especially the get_app_template_dir function above).  So instead I'm going through
# settings.INSTALLED_APPS.  I also can't put this directly in a regular AppConfig subclass because
# app code can call get_app_template_dir above in their ready() calls.  We don't really need
# the other apps to be setup to run this, so it isn't a problem to go straight to INSTALLED_APPS.



class RenderShortcut(object):
  '''A shortcut way to call render() for an app's template renderer.
     The code in this class is a bit convoluted, but it makes it possible
     to call each app's renderer with a function rather than having to get
     an object reference.  This allows DMP to mimick the way Django's native
     render() and render_to_response() methods work.
  '''
  def __init__(self, app_name, method_name):
    self.app_name = app_name
    self.method_name = method_name
    
  def __call__(self, *args, **kwargs):
    '''Allows instances of this class to act like functions.'''
    # I use get_renderer to essentially do "late binding" to the map, just in
    # case the TEMPLATE_RENDERERS map must be modified after its initial creation
    # below.  This way I don't have a direct (and permanent) pointer to the renderer.
    return getattr(get_renderer(self.app_name), self.method_name)(*args, **kwargs)
    


def get_app_template_dir(app_name, template_subdir="templates"):
  '''Checks whether an app seems to be a valid Django-Mako-Plus app, then returns its template directory
     Raises an ImproperlyConfigured exception if the app is not set up as a DMP app.
  '''
  try:
    module_obj = import_module(app_name)
  except ImportError:
    raise ImproperlyConfigured('DMP :: Cannot create MakoTemplateRenderer: App %s does not exist.' % app_name)
  try:
    if not module_obj.DJANGO_MAKO_PLUS:
      raise ImproperlyConfigured('DMP :: Cannot create MakoTemplateRenderer: %s.DJANGO_MAKO_PLUS must be True.' % app_name)
  except AttributeError:
    raise ImproperlyConfigured('DMP :: Cannot create MakoTemplateRenderer: App %s must define DJANGO_MAKO_PLUS=True.' % app_name)
  template_dir = os.path.abspath(os.path.join(os.path.dirname(module_obj.__file__), template_subdir))
  if not os.path.isdir(template_dir):
    raise ImproperlyConfigured('DMP :: Cannot create MakoTemplateRenderer: App %s has no templates folder (it needs %s).' % (app_name, template_dir))
  return template_dir



   
# go through each app in INSTALLED_APPS and find the DMP-enabled apps
for app_name in settings.INSTALLED_APPS:
  try:
    # get the module so we can add the shortcuts
    module_obj = import_module(app_name)
    # this method checks whether it's a valid DMP app
    get_app_template_dir(app_name)
    # add a renderer to the cache
    TEMPLATE_RENDERERS[app_name] = MakoTemplateRenderer(app_name)
    # add two shortcut "functions" to the app module object to make rendering more accessible in each app
    module_obj.dmp_render = RenderShortcut(app_name, 'render')
    module_obj.dmp_render_to_response = RenderShortcut(app_name, 'render_to_response')
  except (ImproperlyConfigured, ImportError):
    pass # we'll handle these exceptions below in get_renderer() since the app doesn't get added to the TEMPLATE_RENDERERS map


