#!/usr/bin/python
#
#   Author:  Conan Albrecht <ca&byu,edu>
#   License: Apache Open Source License
#   Version: 2013.10.19
#
__doc__ = '''
  This file is used by base_app/templates/base_template.htm to automatically include the .css, .cssm, .js, and .jsm
  files into a template hierarchy.
  
  For example, suppose we have the following template chain:
    Base template: /base_app/templates/base_template.htm
    Child template: /calculator/templates/index.html

  Because of this chain, the following styles and scripts are automatically included in the rendered page:

    /base_app/styles/base.css
    /base_app/styles/base.cssm (this one can contain dynamic Python code)
    /calculator/styles/index.css
    /calculator/styles/index.cssm (this one can contain dynamic Python code)
    /base_app/scripts/base.js
    /base_app/scripts/base.jsm (this one can contain dynamic Python code)
    /calculator/scripts/index.js
    /calculator/scripts/index.jsm (yep, you guessed it, this one can contain dynamic Python code)
    
  This file makes the above happen.  It allows the programmer to separate the HTML, CSS, and JS into separate
  files but still have them serve to the browser together.  It also keeps the CSS and JS together with the HTML
  at each specific level in the template inheritance chain.  
  
  Note that with this Django starter kit, we recreate the static renderer each time.
  At deployment, it would speed things up considerably to cache these StaticRenderer
  objects in a dict or other type of cache.  This isn't done here to keep things simpler.
'''

from django.conf import settings
from django_mako_plus.controller.router import MakoTemplateRenderer
from django_mako_plus.controller import get_setting
import os, os.path, time


DMP_ATTR_NAME = 'dmp_templateinfo'  # used to attach TemplateInfo objects to Mako templates


# Import minification if requested
JSMIN = False
CSSMIN = False
if get_setting('MINIFY_JS_CSS', False) and not settings.DEBUG:
  try:
    from rjsmin import jsmin
    JSMIN = True
  except ImportError:
    pass
  try:
    from rcssmin import cssmin
    CSSMIN = True
  except ImportError:
    pass


#######################################################################
###   A dict of template renderers for scripts and styles in our apps.
###   These are created as needed in TemplateInfo below and cached here.
###   One for each app is created in each dict.

SCRIPT_RENDERERS = {}
STYLE_RENDERERS = {}



#######################################################################
###   Template-specific CSS and JS, both static and mako-rendered

class TemplateInfo(object):
  '''Data class that holds information about a template's directories.  The StaticRenderer
     object below creates a TemplateInfo object for each level in the Mako template inheritance
     chain.
  '''
  def __init__(self, template, cgi_id=None):
    # set up the directories so we can go through them fast on render
    self.template_dir, self.template_name = os.path.split(os.path.splitext(template.filename)[0])
    self.app_dir = os.path.dirname(self.template_dir)
    self.app = os.path.split(self.app_dir)[1]
    
    # ensure we have renderers for this template
    if self.app not in SCRIPT_RENDERERS:
      SCRIPT_RENDERERS[self.app] = MakoTemplateRenderer(self.app, 'scripts')
    if self.app not in STYLE_RENDERERS:
      STYLE_RENDERERS[self.app] = MakoTemplateRenderer(self.app, 'styles')

    # the static templatename.css file
    try:
      fstat = os.stat(os.path.join(self.app_dir, 'styles', self.template_name + '.css'))
      self.css = '<link rel="stylesheet" type="text/css" href="%s?%s" />' % (os.path.join(settings.STATIC_URL, self.app, 'styles', self.template_name + '.css'), cgi_id if cgi_id != None else int(fstat.st_mtime))
    except IOError:
      self.css = None

    # the mako-rendered templatename.cssm file
    try:
      fstat = os.stat(os.path.join(self.app_dir, 'styles', self.template_name + '.cssm'))
      self.cssm = self.template_name + '.cssm'
    except IOError:
      self.cssm = None

    # the static templatename.js file
    try:
      fstat = os.stat(os.path.join(self.app_dir, 'scripts', self.template_name + '.js'))
      self.js = '<script src="%s?%s"></script>' % (os.path.join(settings.STATIC_URL, self.app, 'scripts', self.template_name + '.js'), cgi_id if cgi_id != None else int(fstat.st_mtime))
    except IOError:
      self.js = None

    # the mako-rendered templatename.jsm file
    try:
      fstat = os.stat(os.path.join(self.app_dir, 'scripts', self.template_name + '.jsm'))
      self.jsm = self.template_name + '.jsm'
    except IOError:
      self.jsm = None


class StaticRenderer(object):
  '''Renders the styles and scripts for a given template. 
     
     The mako_self parameter is simply the "self" variable
     accessible within any Mako template.  An example call is:
     
     <%! from django_mako_plus.controller import static_files %>
     <%  static_renderer = static_files.StaticRenderer(self) %>
     
     The optional cgi_id parameter is a less obvious.  On some browsers, 
     new CSS/JS files don't load because the browser waits for 7 (or whatever) days
     to check for a new version.  This value is set by your web server,
     and it's normally a good thing to speed everything up.  However,
     when you upload new CSS/JS, you want all browsers to download the new
     files even if their cached versions have't expired yet.  

     By adding an arbitrary id to the end of the .css and .js files, browsers will
     see the files as *new* anytime that id changes.  The default method 
     for calculating the id is the file modification time (minutes since 1970). 
  '''
  def __init__(self, mako_self, cgi_id=None):
    self.mako_self = mako_self
    self.template_chain = []
    # step up the template inheritance chain and ensure each template has a TemplateInfo object
    # I attach it to the template objects because they are cached by mako (and thus we take 
    # advantage of that caching).
    while mako_self != None:
      if settings.DEBUG or not hasattr(mako_self.template, DMP_ATTR_NAME):  # always recreate in debug mode
        setattr(mako_self.template, DMP_ATTR_NAME, TemplateInfo(mako_self.template))
      self.template_chain.append(mako_self.template)  
      mako_self = mako_self.inherits
    

  def get_template_css(self, request, context):
    '''Retrives the static and mako-rendered CSS'''
    ret = []
    for template in reversed(self.template_chain):  # reverse so lower CSS overrides higher CSS in the inheritance chain
      ti = getattr(template, DMP_ATTR_NAME)
      if ti.css:
        ret.append(ti.css)  # the <link> was already created once in the constructor
      if ti.cssm:
        css_text = STYLE_RENDERERS[ti.app].render(request, ti.cssm, context.kwargs)
        if JSMIN and get_setting('MINIFY_JS_CSS', False):
          css_text = cssmin(css_text)
        ret.append('<style type="text/css">%s</style>' % css_text) 
    return '\n'.join(ret)


  def get_template_js(self, request, context):
    '''Retrieves the static and mako_rendered CSS'''    
    ret = []
    for template in self.template_chain:
      ti = getattr(template, DMP_ATTR_NAME)
      if ti.js:
        ret.append(ti.js)  # the <script> was already created once in the constructor
      if ti.jsm:
        js_text = SCRIPT_RENDERERS[ti.app].render(request, ti.jsm, context.kwargs)
        if JSMIN and get_setting('MINIFY_JS_CSS', False):
          js_text = jsmin(js_text)
        ret.append('<script>%s</script>' % js_text)
    return '\n'.join(ret)


