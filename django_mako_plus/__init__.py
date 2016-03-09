#
#   Author:  Conan Albrecht <ca&byu,edu>
#   License: Apache Open Source License
#


# The version of DMP - used by sdist to publish to PyPI
__version__ = '2.7.1'



from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect




###############################################################
###   Gets the specified setting.  During 2015, we changed the
###   way settings are specified in the settings.py file to
###   a dictionary.  This is a temporary fix to support both
###   ways of doing it.

def get_setting(name, default=None):
  # the new way
  try:
    return settings.DJANGO_MAKO_PLUS[name]
    
  except KeyError:
    if default != None:
      return default
    raise ImproperlyConfigured('The settings.DJANGO_MAKO_PLUS dict did not have a setting named %s.' % (name))
    
  except AttributeError:
    pass  # move on to old way
    
  # the old way
  try:
    return getattr(settings, 'DMP_%s' % name)
  except AttributeError:
    if default != None:
      return default
    raise ImproperlyConfigured('The settings.py file needs to set DMP_%s.' % (name))




   
###############################################################
###   A decorator that signals that a function is callable
###   by DMP.  This prevents "just any function" from being 
###   called by the router above.  The function must be
###   decorated to be callable:
###
###       @view_function
###       function process_request(request):
###           ...   

    
def view_function(f):    
  '''A decorator to signify which view functions are "callable" by web browsers.
     This decorator is more of an annotation on functions than a decorator.
     Rather than the usual inner function pattern, I'm simply setting a flag on the
     function to signify that it is callable.  The router checks this flag
     before calling the function.
  '''
  f.dmp_view_function = True
  return f

    

###############################################################
###   Exceptions used to direct the controller


class InternalRedirectException(Exception):
  '''View functions can throw this exception to indicate that a new view
     should be called by the HtmlPageServer.  The current view function
     will end immediately, and processing will be passed to the new view function.
  '''
  def __init__(self, redirect_module, redirect_function):
    '''Indicates the new view to be called.  The view should be given relative to the project root.
       The parameters should be strings, not the actual module or function reference.
    '''
    super(InternalRedirectException, self).__init__()
    self.redirect_module = redirect_module
    self.redirect_function = redirect_function
  



class RedirectException(Exception):
  '''Immediately stops processing of a view function or template and redirects to the given page.
     Perhaps it takes a little too much liberty with exceptions, but it makes returning from a 
     huge call stack really nice.

     If as_javascript==True, the browser is sent <script>window.location.href="...";</script>.
     This is useful when using Ajax.  A redirect in Ajax is handled internally by libraries like
     JQuery, so a regular HTTP redirect can't direct the top-level page.  Javascript is a hack
     around this so an Ajax call can redirect the whole browser window.
  '''
  def __init__(self, redirect_to, permanent=False, as_javascript=False):
    self.redirect_to = redirect_to
    self.permanent = permanent
    self.as_javascript = as_javascript
    

  def get_response(self, request):
    '''Returns the redirect response for this exception.  DMP passes the current request
       as a parameter for your convenience in using the user object, session object, etc.'''
    if self.as_javascript:
      return HttpResponse('<script>window.location.href="%s";</script>' % self.redirect_to)
    if self.permanent:
      return HttpResponsePermanentRedirect(self.redirect_to)
    return HttpResponseRedirect(self.redirect_to)



