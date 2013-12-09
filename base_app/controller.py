#!/usr/bin/python
#
#   Author:  Conan Albrecht <ca&byu,edu>
#   License: Apache Open Source License
#   Version: 2013.10.19
#

from django.core.urlresolvers import get_mod_func
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.conf import settings
from django.template import RequestContext
from mako.exceptions import TopLevelLookupException, html_error_template
from mako.lookup import TemplateLookup
import os, os.path, re, mimetypes, importlib
import urllib.request, urllib.parse, urllib.error


# set up the logger
import logging 
log = logging.getLogger('django')


##############################################################
###   The front controller of all views on the site.
###   urls.py routes everything through this method.

def route_request(request):
    '''The main router for all calls coming in to the system.'''
    # output the variables so the programmer can debug where this is routing
    log.debug('base_app.controller.py :: HtmlPageServer processing: app=%s, page=%s, funcname=%s, urlparams=%s' % (request.controller_app, request.controller_page, request.controller_funcname, request.urlparams))

    # first try going to the view function for this request
    # we look for a views/name.py file where name is the same name as the HTML file
    response = None
    request.controller_view_function = 'process_request%s' % (request.controller_funcname)
    request.controller_view_module = '.'.join([ request.controller_app, 'views', request.controller_page ])
    
    # this next line assumes that base_app.controller.py is one level below the settings.py file (hence the '..')
    full_module_filename = os.path.normpath(os.path.join(settings.BASE_DIR, request.controller_view_module.replace('.', '/') + '.py'))
    while True:
      try:
        # look for the module
        if os.path.exists(full_module_filename):
          module_obj = importlib.import_module(request.controller_view_module)
          if hasattr(module_obj, request.controller_view_function):
            log.debug('base_app.controller.py :: calling view function %s.%s' % (request.controller_view_module, request.controller_view_function))
            try: 
              response = getattr(module_obj, request.controller_view_function)(request)
            except RedirectException as e: # redirect to another page
              log.debug('base_app.controller.py :: view function %s.%s redirected processing to %s' % (request.controller_view_module, request.controller_view_function, e.redirect_to))
              if e.permanent:
                return HttpResponsePermanentRedirect(e.redirect_to)
              return HttpResponseRedirect(e.redirect_to)
          else:
            log.debug('base_app.controller.py :: view function %s not in module %s; returning 404 not found' % (request.controller_view_function, request.controller_view_module))
            raise Http404
        else:
          log.debug('base_app.controller.py :: module %s not found; sending processing directly to the template' % (request.controller_view_module))
        break
      except InternalViewRedirectException as ivr:
        request.controller_view_module = ivr.redirect_module
        request.controller_view_function = ivr.redirect_function
        full_module_filename = os.path.normpath(os.path.join(settings.BASE_DIR, request.controller_view_module.replace('.', '/') + '.py'))
        log.debug('base_app.controller.py :: received an InternalViewRedirect to %s -> %s' % (full_module_filename, request.controller_view_function))
      
    # if we get here, a matching view wasn't found; look for a matching template
    if response == None and request.controller_app in TEMPLATE_RENDERERS:
        response = TEMPLATE_RENDERERS[request.controller_app].render_to_response(request, '%s.html' % request.controller_page)
  
    # return the response
    if response == None:
      raise Http404
      
    return response  
    
    

    

###############################################################
###   Exceptions used to direct the base_app.controller

class InternalViewRedirectException(Exception):
  '''View functions can throw this exception to indicate that a new view
     should be called by the HtmlPageServer.  The current view function
     will end immediately, and processing will be passed to the new view function.
  '''
  def __init__(self, redirect_module, redirect_function):
    '''Indicates the new view to be called.  The view should be given relative to the project root.'''
    super().__init__()
    self.redirect_module = redirect_module
    self.redirect_function = redirect_function
  

class TemplateException(Exception):
  '''A template exception while rendering Mako templates'''
  def __init__(self, error, message):
    self.error = error
    Exception.__init__(self, message)


class RedirectException(Exception):
  '''Immediately stops processing of a view function or template and redirects to the given page.
     Note that this exception only works when urls.py routes the call through the classes in this
     module.  Django should have shipped with this one.  Perhaps it takes a little too much liberty
     with exceptions, but it makes returning from a huge call stack really nice.'''
  def __init__(self, redirect_to, permanent=False):
    self.redirect_to = redirect_to
    self.permanent = permanent




##############################################################
###   Renders Mako templates

class MakoTemplateRenderer:
  '''Renders Mako templates.  Note that the following defaults are used:
       templates_dir  => project_path/app_path/templates/  (assuming settings.base_app.controller_TEMPLATES_DIR is set to 'templates')
       cache_dir      => project_path/template_cache/      (assuming settings.MAKO_TEMPLATES_CACHE_DIR is set to 'template_cache/applications/)
       cache_size     => 2000
  '''
  def __init__(self, app_path, template_subdir='templates'):
    '''Creates a renderer to the given path (relateive to the project root where settings.STATIC_ROOT points to)'''
    project_path = os.path.normpath(settings.BASE_DIR)
    self.app_path = app_path
    self.template_search_dirs = [ os.path.abspath(os.path.join(project_path, self.app_path, template_subdir)) ] + settings.MAKO_TEMPLATES_DIRS
    self.cache_root = os.path.abspath(os.path.join(project_path, app_path, settings.MAKO_TEMPLATES_CACHE_DIR, template_subdir)) 
    self.tlookup = TemplateLookup(directories=self.template_search_dirs, imports=settings.MAKO_DEFAULT_TEMPLATE_IMPORTS, module_directory=self.cache_root, collection_size=2000, filesystem_checks=settings.DEBUG)


  def render(self, request, template, params={}):
    '''Runs a template and returns a string.  Normally, you probably want to call render_to_response instead
       because it gives a full HttpResponse or Http404.
       
       This method raises a TopLevelLookupException if the template is not found.
    
       @request  The context request from Django
       @template The template file path to render.  This is relative to the app_path/base_app.controller_TEMPLATES_DIR/ directory.
                 For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                 set up the variables as described in the documentation above.
       @params   A dictionary of name=value variables to send to the template page.
       
    '''
    # Django's RequestContext automatically runs all the TEMPLATE_CONTEXT_PROCESSORS and populates with variables
    context = RequestContext(request, params)
    context_dict = { 'request': request, 'settings': settings }  # this allows the template to access the request
    # must convert the request context to a real dict to use the ** below
    for d in context:
      context_dict.update(d)
    # render the response with the given template and params
    template_obj = self.tlookup.get_template(template)
    if not hasattr(template_obj, 'template_path'):
      template_obj.template_path = template
    if not hasattr(template_obj, 'template_full_path'):
      template_obj.template_full_path = template_obj.filename
    if not hasattr(template_obj, 'mako_template_renderer'):  # if the first time, add a reference to this renderer object
      template_obj.mako_template_renderer = self
    log.debug('base_app.controller.py :: rendering template %s' % template_obj.filename)
    if settings.DEBUG:
      try:
        return template_obj.render_unicode(**context_dict)
      except:
        return html_error_template().render_unicode()
    else:
      return template_obj.render_unicode(**context_dict)
    
    
  def render_to_response(self, request, template, params={}):
    '''Runs a template and returns an HttpRequest object to it. 
    
       @request  The context request from Django
       @template The template file path to render.  This is relative to the app_path/base_app.controller_TEMPLATES_DIR/ directory.
                 For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                 set up the variables as described in the documentation above.
       @params   A dictionary of name=value variables to send to the template page.
    '''
    try:
      content_type = mimetypes.types_map.get(os.path.splitext(template)[1].lower(), 'text/html')
      content = self.render(request, template, params)
      return HttpResponse(content.encode(settings.DEFAULT_CHARSET), content_type='%s; charset=%s' % (content_type, settings.DEFAULT_CHARSET))
    except TopLevelLookupException: # template file not found    
      log.debug('base_app.controller.py :: template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
      raise Http404()
    except RedirectException as e: # redirect to another page
      if e.permanent:
        return HttpResponsePermanentRedirect(e.redirect_to)
      return HttpResponseRedirect(e.redirect_to)


# these are the apps we can render templates for - it is used in route_request at the top
TEMPLATE_RENDERERS = {}
for appname in settings.MAKO_ENABLED_APPS:
  TEMPLATE_RENDERERS[appname] = MakoTemplateRenderer(appname)




##########################################################
###   Middleware the prepares the request for
###   use with the base_app.controller

class RequestInitMiddleware:
  '''Adds several fields to the request that our base_app.controller needs.
  
     This class MUST be included in settings.py -> MIDDLEWARE_CLASSES.
  '''
  
  def process_request(self, request):
    '''Called for each browser request.  This adds the following fields to the request object:
    
       request.controller_app       The Django application (such as "calculator").
       request.controller_page      The view module (such as "calc" for calc.py).
       request.controller_funcname  The function within the view module to be called (usually "process_request").
       request.urlparams            A list of the remaining url parts (see the calc.py example).
    '''
    # split the path
    path_parts = request.path[1:].split('/') # [1:] to remove the leading /
      
    # get the app
    if len(path_parts) >= 1 and path_parts[0] == '':  # app specified by empty, so revert to default app
      path_parts[0] = settings.MAKO_DEFAULT_APP
    elif len(path_parts) < 1 or path_parts[0] not in settings.MAKO_ENABLED_APPS:  # app not specified, or invalid app, so insert the default app into the path_parts
      path_parts.insert(0, settings.MAKO_DEFAULT_APP)
    request.controller_app = path_parts[0]
      
    # get the page
    if len(path_parts) < 2:  # page not specified, so insert the default page into the path_parts (we'll validate later in the controller)
      path_parts.insert(1, settings.MAKO_DEFAULT_PAGE)
    elif path_parts[1] == '':  # page specified by empty
      path_parts[1] = settings.MAKO_DEFAULT_PAGE
    request.controller_page = path_parts[1]
    
    # see if a function is specified with the page (the __ separates a function name)
    du_pos = request.controller_page.find('__')
    if du_pos < 0:
      request.controller_funcname = ''
    else:
      request.controller_funcname = request.controller_page[du_pos:]
      request.controller_page = request.controller_page[:du_pos]
      
    # set up the urlparams with the reamining path parts
    request.urlparams = URLParamList([ urllib.parse.unquote_plus(s) for s in path_parts[2:] ])
    
        


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
  
