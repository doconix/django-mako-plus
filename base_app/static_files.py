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
from base_app.controller import MakoTemplateRenderer
import os, os.path, time


######################################################################
###  Get the minute the server started.  On some browsers, new CSS/JS
###  doesn't load because the browser waits for 7 (or whatever) days
###  to check for a new version.  This value is set by your web server,
###  and it's normally a good thing to speed everything up.  However,
###  when you upload new CSS/JS, you want all browsers to download the new
###  files even if their cached version hasn't expired yet.
###
###  By adding an int to the end of the .css and .js files, browsers will
###  see the files as *new* every time you restart your web server.
SERVER_START_MINUTE = int(time.time() / 60)  # minutes since Jan 1, 1970


#######################################################################
###   A dict of template renderers for scripts and styles in our apps.

SCRIPT_RENDERERS = {}
STYLE_RENDERERS = {}
for appname in settings.MAKO_ENABLED_APPS:
  SCRIPT_RENDERERS[appname] = MakoTemplateRenderer(appname, 'scripts')
  STYLE_RENDERERS[appname] = MakoTemplateRenderer(appname, 'styles')



#######################################################################
###   Template-specific CSS and JS, both static and mako-rendered

class TemplateInfo(object):
  '''Data class that holds information about a template's directories.  The StaticRenderer
     object below creates a TemplateInfo object for each level in the Mako template inheritance
     chain.
  '''
  def __init__(self, template):
    # set up the directories so we can go through them fast on render
    self.template_dir, self.template_name = os.path.split(os.path.splitext(template.filename)[0])
    self.app_dir = os.path.dirname(self.template_dir)
    self.app = os.path.split(self.app_dir)[1]
    # the static templatename.css file
    self.css = None
    if os.path.exists(os.path.join(self.app_dir, 'styles', self.template_name + '.css')):
      self.css = '<link rel="stylesheet" type="text/css" href="%s?%i" />' % (os.path.join(settings.STATIC_URL, self.app, 'styles', self.template_name + '.css'), SERVER_START_MINUTE)
    # the mako-rendered templatename.cssm file
    self.cssm = None
    if os.path.exists(os.path.join(self.app_dir, 'styles', self.template_name + '.cssm')):
      self.cssm = self.template_name + '.cssm'
    # the static templatename.js file
    self.js = None
    if os.path.exists(os.path.join(self.app_dir, 'scripts', self.template_name + '.js')):
      self.js = '<script src="%s?%i"></script>' % (os.path.join(settings.STATIC_URL, self.app, 'scripts', self.template_name + '.js'), SERVER_START_MINUTE)
    # the mako-rendered templatename.jsm file
    self.jsm = None
    if os.path.exists(os.path.join(self.app_dir, 'scripts', self.template_name + '.jsm')):
      self.jsm = self.template_name + '.jsm'
    

class StaticRenderer(object):
  '''The styles and scripts for a given template.'''
  def __init__(self, mako_self):
    # get the inheritance chain for this template
    self.template_infos = []
    while mako_self != None:
      self.template_infos.insert(0, TemplateInfo(mako_self.template))  # go in reversed order so the most specialized template CSS/JS prints last and wins in a conflict
      mako_self = mako_self.inherits


  def get_template_css(self, request, context):
    '''Retrives the static and mako-rendered CSS'''
    ret = []
    for ti in self.template_infos:
      if ti.css:
        ret.append(ti.css)  # the <link> was already created once in the constructor
      if ti.cssm:
        ret.append('<style type="text/css">%s</style>' % STYLE_RENDERERS[ti.app].render(request, ti.cssm, context.kwargs)) 
    return '\n'.join(ret)


  def get_template_js(self, request, context):
    '''Retrieves the static and mako_rendered CSS'''    
    ret = []
    for ti in self.template_infos:
      if ti.js:
        ret.append(ti.js)  # the <script> was already created once in the constructor
      if ti.jsm:
            ret.append('<script>%s</script>' % SCRIPT_RENDERERS[ti.app].render(request, ti.jsm, context.kwargs))
    return '\n'.join(ret)


