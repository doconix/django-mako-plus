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
from .exceptions import SassCompileException
from .util import run_command, get_dmp_instance, get_dmp_option, log
import os, os.path, posixpath, subprocess


# keys to cache these the static renderer for a small speedup
DMP_TEMPLATEINFO_KEY = 'django_mako_plus_templateinfo'
DMP_STATIC_RENDERER_KEY = 'django_mako_plus_staticrenderer'




#######################################################################
###   Shortcut methods - these are the primary way the static render
###   shoudl be used

def get_template_css(mako_self, request, context, cgi_id=None):
    '''Renders the styles for a given template.

       The mako_self parameter is simply the "self" variable
       accessible within any Mako template.  An example call is:

       <%! from django_mako_plus import get_template_css %>
       ${ get_template_css(self, request, context) }

       See StaticRenderer below for a description of cgi_id.
    '''
    return _get_cached_static_renderer(mako_self, cgi_id).get_template_css(request, context)


def get_template_js(mako_self, request, context, cgi_id=None):
    '''Renders the scripts for a given template.

       The mako_self parameter is simply the "self" variable
       accessible within any Mako template.  An example call is:

       <%! from django_mako_plus import get_template_js %>
       ${ get_template_js(self, request, context) }

       See StaticRenderer below for a description of cgi_id.
    '''
    return _get_cached_static_renderer(mako_self, cgi_id).get_template_js(request, context)


def _get_cached_static_renderer(mako_self, cgi_id=None):
    '''Internal method to get/cache a template renderer in the current mako_self'''
    try:
        return getattr(mako_self, DMP_STATIC_RENDERER_KEY)
    except AttributeError:
        static_renderer = StaticRenderer(mako_self, cgi_id)
        setattr(mako_self, DMP_STATIC_RENDERER_KEY, static_renderer)
        return static_renderer



#######################################################################
###   Template-specific CSS and JS, both static and mako-rendered

class TemplateInfo(object):
    '''Data class that holds information about a template's directories.  The StaticRenderer
       object below creates a TemplateInfo object for each level in the Mako template inheritance
       chain.  This object is then attached to the template object, which Mako already caches.
       That way we only do this work once per server run (in production mode).

       The app_dir is the search location for the styles/ and scripts/ folders, relative to the
       project base directory.  For typical apps, this is simply the app name.

       The template_filename is the filename of the template.

       The cgi_id parameter is described in the MakoTemplateRenderer class below.
    '''
    def __init__(self, app_dir, template_filename, cgi_id=None):
        # I want short try blocks, so there are several - for example, the first OSError can only occur for one reason: if the os.stat() fails.
        # I'm using os.stat here instead of os.path.exists because I need the st_mtime.  The os.stat checks that the file exists and gets the modified time in one command.
        self.template_name = os.path.splitext(template_filename)[0]  # remove its extension
        self.app_dir = app_dir
        self.app = os.path.split(self.app_dir)[1]

        # set up the filenames
        css_file = os.path.join(self.app_dir, 'styles', '%s.css' % self.template_name)
        cssm_file = os.path.join(self.app_dir, 'styles', '%s.cssm' % self.template_name)
        js_file = os.path.join(self.app_dir, 'scripts', '%s.js' % self.template_name)
        jsm_file = os.path.join(self.app_dir, 'scripts', '%s.jsm' % self.template_name)

        # the SASS templatename.scss (compile any updated templatename.scss files to templatename.css files)
        if get_dmp_option('RUNTIME_SCSS_ENABLED'):
            scss_file = os.path.join(self.app_dir, 'styles', '%s.scss' % self.template_name)
            try:
                scss_stat = os.stat(scss_file)
            except OSError:
                scss_stat = None
            if scss_stat != None:  # only continue this block if we found a .scss file
                try:
                    fstat = os.stat(css_file)
                except OSError:
                    fstat = None
                # if we 1) have no css_file or 2) have a newer scss_file, run the compiler
                if fstat == None or scss_stat.st_mtime > fstat.st_mtime:
                    try:
                        run_command(get_dmp_option('RUNTIME_SCSS_ARGUMENTS') + [ scss_file, css_file ])
                    except subprocess.CalledProcessError as cpe:
                        raise SassCompileException(cpe.cmd, cpe.stderr)

        # the static templatename.css file
        try:
            fstat = os.stat(css_file)
            self.css = '<link rel="stylesheet" type="text/css" href="%s?%s" />' % (posixpath.join(settings.STATIC_URL, self.app, 'styles', self.template_name + '.css'), cgi_id if cgi_id != None else int(fstat.st_mtime))
        except OSError:
            self.css = None

        # the mako-rendered templatename.cssm file
        try:
            fstat = os.stat(cssm_file)
            self.cssm = self.template_name + '.cssm'
        except OSError:
            self.cssm = None

        # the static templatename.js file
        try:
            fstat = os.stat(js_file)
            self.js = '<script src="%s?%s"></script>' % (posixpath.join(settings.STATIC_URL, self.app, 'scripts', self.template_name + '.js'), cgi_id if cgi_id != None else int(fstat.st_mtime))
        except OSError:
            self.js = None

        # the mako-rendered templatename.jsm file
        try:
            fstat = os.stat(jsm_file)
            self.jsm = self.template_name + '.jsm'
        except OSError:
            self.jsm = None


    def get_template_css(self, request, context):
        '''Returns the CSS for this template's .css and .cssm files, if they exist.'''
        ret = []
        # do we have a css?
        if self.css:
            ret.append(self.css)  # the <link> was already created once in the constructor
        # do we have a cssm?
        if self.cssm:
            lookup = get_dmp_instance().get_template_loader(self.app, 'styles')
            css_text = lookup.get_template(self.cssm).render(request=request, context=context)
            if get_dmp_option('RUNTIME_CSSMIN'):
                css_text = cssmin(css_text)
            ret.append('<style type="text/css">%s</style>' % css_text)
        # join and return
        return '\n'.join(ret)


    def get_template_js(self, request, context):
        '''Returns the Javascript for this template's .js and .jsm files, if they exist.'''
        ret = []
        # do we have a js?
        if self.js:
            ret.append(self.js)  # the <script> was already created once in the constructor
        # do we have a jsm?
        if self.jsm:
            lookup = get_dmp_instance().get_template_loader(self.app, 'scripts')
            js_text = lookup.get_template(self.jsm).render(request=request, context=context)
            if get_dmp_option('RUNTIME_JSMIN'):
                js_text = jsmin(js_text)
            ret.append('<script>%s</script>' % js_text)
        # join and return
        return '\n'.join(ret)





class StaticRenderer(object):
    '''Renders the styles and scripts for a given template.

       The mako_self parameter is simply the "self" variable
       accessible within any Mako template.  An example call is:

       <%! from django_mako_plus import static_files %>
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
            if settings.DEBUG or not hasattr(mako_self.template, DMP_TEMPLATEINFO_KEY):  # always recreate in debug mode
                template_dir, template_name = os.path.split(mako_self.template.filename)
                app_dir = os.path.dirname(template_dir)
                setattr(mako_self.template, DMP_TEMPLATEINFO_KEY, TemplateInfo(app_dir, template_name))
            self.template_chain.append(mako_self.template)
            mako_self = mako_self.inherits


    def get_template_css(self, request, context):
        '''Retrives the static and mako-rendered CSS for the entire template chain'''
        ret = []
        for template in reversed(self.template_chain):  # reverse so lower CSS overrides higher CSS in the inheritance chain
            ret.append(getattr(template, DMP_TEMPLATEINFO_KEY).get_template_css(request, context.kwargs))
        return '\n'.join(ret)


    def get_template_js(self, request, context):
        '''Retrieves the static and mako_rendered CSS for the entire template chain'''
        ret = []
        for template in self.template_chain:
            ret.append(getattr(template, DMP_TEMPLATEINFO_KEY).get_template_js(request, context.kwargs))
        return '\n'.join(ret)
