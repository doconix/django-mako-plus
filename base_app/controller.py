#!/usr/bin/python
#
#   Author:  Conan Albrecht <ca&byu,edu>
#   License: Apache Open Source License
#   Version: 2013.10.19
#
__doc__ = '''
                                      DESCRIPTION
                             
  NOTE: I wrote an extended HOWTO on this module at http://warp.byu.edu/site/content/907.
  See that link for a detailed walkthrough in setting up Django, Apache, and Mako.                           
                                      
  An extension to Django to use Mako templates rather than the built-in Django templates.  Why
  use Mako instead of Django's built-in template language?  Because while most of Django is
  wonderful, the template language is weak sauce.  In fact, Django shamelessly points out that
  it keeps the template language simple to encourage developers to use views for functionality.
  I agree that logic should be kept to views, but I already have to learn HTML, Javascript, JQuery,
  Python, Django, and a host of other languages to make this all work.  Now they want to throw
  another language into the mix--for no other reason than to encourage me to behave?  No thanks.
  
  Mako is strong sauce: it uses Python itself for the templating language.  All the power and ease 
  of Python, right within the web page.  And Mako integrates with Django easily.  This module
  is the glue that binds Django and Mako together in one happy family.

  In particular, this module provides the following two things:  
  
  1. Defines the MakoTemplateRenderer object, which runs a Mako template.  Any view function
     can call this method to render a template.  Example views.py:

     import base_app.controller
     templater = base_app.controller.MakoTemplateRenderer('thisappname')  # only need one of these per app
     
     def myview(request):
       # a bunch of processing here
       # now render the template called "mytemplate.html", sending paramA and paramB as variables
       return templater.render_to_response(request, 'mytemplate.html', { 'paramA': 'asdf', 'paramB': 0 })

     If all you want to do is use Mako for your Django templating and do everything else the Django way, 
     you can stop reading here.  The above code makes it work.  #2 below is only a shortcut that makes
     calling views easier -- with it, you can shorten your urls.py file.

  2. Defines the HtmlPageServer class, which serves any view and any template file.  Django normally
     requires that every page in the program have a urls.py entry.  This is stupid, since a simple
     notation can call pages automatically from a controller like this.  To enable
     this, add the following to your urls.py file for each app (change appname to your app name):
  
        # matches a totally empty url (goes to default app, default page)
        (r'^$', 'extensions.base_app.controller.route_request' ),

        # matches url with app and page (path, func, urlparams optional):
        #  app/path/to/module/page.func/param1/param2/param3
        #  app/page.func/param1/param2
        #  app/page/param1/param2
        #  app/page
        (r'^(?P<app>[^/]+?)(?P<page>/[^/]+?)?(?P<func>__[^/]+)?(?P<urlparams>/.*)?$', 'extensions.base_app.controller.route_request' ),

     URLs are provided in /appname/pagename__funcname/param1/param2/param3/ format.  This has three parts:
       - The path name is everything up to the .html (per the regex in urls.py). The path name specifies the
         module look in.  Any periods in the path name are replaced with underscores (since Python doesn't allow 
         periods in module or function names).
       - The function to call is specified after two underscores.  This is optional.  If no double-underscores are given, 
         the standard function 'process_request' is called in the module.  If a function name is specified,
         process_request__functionname is called.  The static string 
         'process_request__' is added to the front of the function name for security. That way module functions are 
         protected from access via the web except those explicitly made available with a name starting with process_request.
       - Parameters can be provided, separated by slashes.  These parameters are placed in a list and attached to the request
         object as request.urlparams.  These are an alternative to standard, named parameters (name=value),
         and they are purely for asthetics -- these type of parameters just make URLs prettier.

     Following are some examples of URLs and their processing:
     
       Regular process:
       /appname/pagename
         Module    = views/pagename.py
         Function  = process_request(request)
                     If this module or function is not found, templates/pagename.html is rendered through Mako.
              
       Regular Process with module in subdirectory of views/:
       /appname/mymod/pagename
         Module    = views/mymod/pagename.py
         Function  = process_request(request)
                     If this module or function is not found, templates/mymod/pagename is rendered through Mako.

       Regular process with custom function name and urlparams:       
       /appname/pagename__funcname/1/2/3/4/
         Module    = views/pagename.py
         Function  = process_request__funcname(request)
                     If this module or function is not found, templates/pagename.html is rendered through Mako.
                     [ '1', '2', '3', '4', ''] is available via request.urlparams.
         
       Regular process with urlparams and regular params:
       /appname/pagename/abc/def?name1=val1&name2=val2
         Module    = views/pagename.py
         Function  = process_request(request)
                     If this mdoule or function is not found, templates/pagename.html is rendered through Mako.
                     { 'name1': 'val1', 'name2': 'val2' } is available via request.REQUEST like normal
                     [ 'abc', 'def' ] is available via request.urlparams.
        
   This assumes the request_init middleware is installed:
     MIDDLEWARE_CLASSES = (
         ...
         'extensions.request_init.RequestInitMiddleware',
     )
           
                  
'''

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
    full_module_filename = os.path.normpath(os.path.join(settings.MAKO_PROJECT_ROOT, request.controller_view_module.replace('.', '/') + '.py'))
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
        full_module_filename = os.path.normpath(os.path.join(settings.MAKO_PROJECT_ROOT, request.controller_view_module.replace('.', '/') + '.py'))
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
    project_path = os.path.normpath(settings.MAKO_PROJECT_ROOT)
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
    # split the path and ensure we have at least two valid items
    path_parts = request.path[1:].split('/') # remove the leading /
    if len(path_parts) < 2:
      raise Http404()  # instead of a 404 error, you could specify a default app and page here.
      
    # set up the app, page, and urlparams variables
    request.controller_app = path_parts[0]
    request.controller_page = path_parts[1]
    du_pos = request.controller_page.find('__')
    if du_pos < 0:
      request.controller_funcname = ''
    else:
      request.controller_funcname = request.controller_page[du_pos:]
      request.controller_page = request.controller_page[:du_pos]
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
  
