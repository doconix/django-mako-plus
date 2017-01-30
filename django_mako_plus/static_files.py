from django.conf import settings
from django.apps import apps
from django.template import TemplateDoesNotExist

from mako.exceptions import MakoException
import mako.runtime

from .sass import check_template_scss
from .exceptions import SassCompileException
from .util import get_dmp_instance, log, DMP_OPTIONS

import os, os.path, io, posixpath, warnings
from collections import deque




# keys to attach TemplateInfo objects and static renderer to the Mako Template itself
# I attach it to the template objects because they are already cached by mako, so
# caching them again here would result in double-caching.  It's a bit of a
# monkey-patch to set them as attributes in the Mako templates, but it's efficient
# and encapsulated entirely within this file
DMP_TEMPLATEINFO_KEY = '_django_mako_plus_templateinfo'

# a cache to store TemplateInfo objects that didn't have an associated template
# these are normally nonexistent files that were referenced (which we allow)
NO_TSELF_CACHE = {}


#######################################################################
###   Shortcut methods - these are the primary way the static render
###   should be used


def link_css(tself, cgi_id=None):
    '''
    Renders the <style> links for a given template.

        ${ django_mako_plus.link_css(self) }

    This call is normally placed in the <head> section of your base.htm
    template.

    Suppose you have two html files using template inheritance: index.html
    and base.htm.  This method will render the links for all style files
    with the names of either of these two templates.  Up to four files
    are linked/sourced:

        base.htm       Generates a <style> link for app/styles/base.css
            |          and a <style> source for app/styles/base.cssm
            |
        index.html     Generates a <style> link for app/styles/index.css
                       and a <style> source for app/styles/index.cssm

    This call must be made from within a rendering Mako template because
    this is where you have  access to the "self" namespace.

    If you need to render these links outside of a template, see link_template_css()
    below.

    The optional cgi_id parameter is to overcome browser caches.  On some browsers,
    changes to your CSS/JS files don't get downloaded because the browser waits a time
    to check for a new version.  This wait time is set by your web server,
    and it's normally a good thing to speed everything up.  However,
    when you upload new CSS/JS files, you want all browsers to download the new
    files even if their cached versions have't expired yet.
    By adding an arbitrary id to the end of the .css and .js files, browsers will
    see the files as *new* anytime that id changes.  The default method
    for calculating the id is the file modification time (minutes since 1970).
    '''
    html = []
    for ti in reversed(build_templateinfo_chain(tself, cgi_id)):
        ti.append_css(tself.context.get('request'), tself.context, html)
    return '\n'.join(html)


def link_js(tself, cgi_id=None):
    '''
    Renders the <script> links for a given template:

        ${ django_mako_plus.link_js(self) }

    This call is normally placed near the end of your base.htm
    template.

    Suppose you have two html files using template inheritance: index.html
    and base.htm.  This method will render the links for all script files
    with the names of either of these two templates.  Up to four files
    are linked/sourced:

        base.htm       Generates a <script> link for app/scripts/base.js
            |          and a <script> source for app/scripts/base.jsm
            |
        index.html     Generates a <script> link for app/scripts/index.js
                       and a <script> source for app/scripts/index.jsm

    This call must be made from within a rendering Mako template because
    this is where you have  access to the "self" namespace.

    If you need to render these links outside of a template, see link_template_js()
    below.

    The optional cgi_id parameter is to overcome browser caches.  On some browsers,
    changes to your CSS/JS files don't get downloaded because the browser waits a time
    to check for a new version.  This wait time is set by your web server,
    and it's normally a good thing to speed everything up.  However,
    when you upload new CSS/JS files, you want all browsers to download the new
    files even if their cached versions have't expired yet.
    By adding an arbitrary id to the end of the .css and .js files, browsers will
    see the files as *new* anytime that id changes.  The default method
    for calculating the id is the file modification time (minutes since 1970).
    '''
    html = []
    for ti in reversed(build_templateinfo_chain(tself, cgi_id)):
        ti.append_js(tself.context.get('request'), tself.context, html)
    return '\n'.join(html)


def link_template_css(request, app, template_name, context, cgi_id=None, force=True):
    '''
    Renders the styles for the given template in the given app.  Normally,
    link_css() is used to accomplish this in your base template.  This method
    is available when/if you need to generate the links in normal python
    code (rather than within a running template).

    The app can be an AppConfig object or the name of the app.
    The template_name is the name of a file in the app/templates/ directory.

    The related .css/.cssm files are created for the template_name
    even if a nonexistent filename is sent.  This can be useful when
    creating html directly within Python code.
    '''
    html = []
    for ti in reversed(build_templateinfo_chain_by_name(app, template_name, cgi_id, force)):
        ti.append_css(request, context, html)
    return '\n'.join(html)


def link_template_js(request, app, template_name, context, cgi_id=None, force=True):
    '''
    Renders the scripts for the given template in the given app.  Normally,
    link_js() is used to accomplish this in your base template.  This method
    is available when/if you need to generate the links in normal python
    code (rather than within a running template).

    The app can be an AppConfig object or the name of the app.
    The template_name is the name of a file in the app/templates/ directory.

    The related .js/.jsm files are created for the template_name
    even if a nonexistent filename is sent.  This can be useful when
    creating html directly within Python code.
    '''
    html = []
    for ti in reversed(build_templateinfo_chain_by_name(app, template_name, cgi_id, force)):
        ti.append_js(request, context, html)
    return '\n'.join(html)



###########################################################
###   Deprecated as of Jan 2017

def get_template_css(tself, request, context, cgi_id=None):
    warnings.warn('As of DMP 3.8, get_template_css(self, request, context) has been changed to template_css(self).  Please make the necessary adjustments in your base templates.', DeprecationWarning)
    return link_css(tself, cgi_id)


def get_template_js(tself, request, context, cgi_id=None):
    warnings.warn('As of DMP 3.8, get_template_js(self, request, context) has been changed to template_js(self).  Please make the necessary adjustments in your base templates.', DeprecationWarning)
    return link_js(tself, cgi_id)




##############################################################################
###   Builds a chain of TemplateInfo objects, one of each level
###   of the inheritance chain of a template.
###


def build_templateinfo_chain(tself, cgi_id=None):
    '''
    Retrieves a chain of TemplateInfo objects.  The chain is formed by following
    template inheritance through inherit tags: <%inherit file="base_homepage.htm" />

    For efficiency, the templates are ordered with the specialization template first.
    The returned list should usually be reversed() by the calling code to put the
    superclass CSS/JS first (allowing the specialization to override supertemplate styles
    and scripts).

    This function is not normally used directly.  Use the link_css() and link_js()
    functions instead.

    # Example placed in a template, using the self namespace
        %for ti in build_templateinfo_chain(self):
            ...
        %endfor

    '''
    # making a list (instead of generator) because it gets reversed() in functions like link_css()
    chain = []

    # step through the template inheritance
    while tself is not None:
        # first check the cache, creating if necessary
        ti = getattr(tself.template, DMP_TEMPLATEINFO_KEY, None)
        if ti is None:
            template_dir, template_name = os.path.split(tself.template.filename)
            app_dir = os.path.dirname(template_dir)
            ti = TemplateInfo(app_dir, template_name, cgi_id)
            # cache in template if in production mode
            if not settings.DEBUG:
                setattr(tself.template, DMP_TEMPLATEINFO_KEY, ti)
        # append the TemplateInfo
        chain.append(ti)
        # loop with the next inherited template
        tself = tself.inherits

    # return
    return chain


def build_templateinfo_chain_by_name(app, template_name, cgi_id, force=True):
    '''
    Retrieves a chain of TemplateInfo objects.  The chain is formed by following
    template inheritance through inherit tags: <%inherit file="base_homepage.htm" />

    For efficiency, the templates are ordered with the specialization template first.
    The returned list should usually be reversed() by the calling code to put the
    superclass CSS/JS first (allowing the specialization to override supertemplate styles
    and scripts).

    This version of the function is useful for python-generated html
    (i.e. direct view.py output).

    If force is True, the templateinfo chain will be created even if the template_name
    does not exist.  This allows python-generated code to take advantage of DMP's
    automatic CSS/JS rendering even if the code has no template.

    If force is False, Mako errors are raised as they occur.  See:
        mako.exceptions.CompileException
        mako.exceptions.SyntaxException
        mako.exceptions.TemplateLookupException
        mako.exceptions.MakoException (catch-all for all Mako errors)

    # Example placed in any python code:
        for ti in build_templateinfo_chain_by_name('homepage', 'index.html'):
            ...

    '''
    # get the AppConfig
    if isinstance(app, str):
        app = apps.get_app_config(app)

    # try to generate a tself so we can use the normal method
    # this uses Mako caching mechanism, so it's pretty fast
    try:
        template = get_dmp_instance().get_template_loader(app, create=True).get_mako_template(template_name)
        context = _create_empty_mako_context(template)
        return build_templateinfo_chain(context['self'], cgi_id)
    except MakoException: # includes template not found, template syntax error, compile exception, etc.
        if not force:
            raise

    # if we get here, we probably have a nonexistent file (which is allowed)
    key = (app.path, template_name)
    try:
        ti = NO_TSELF_CACHE[key]
    except KeyError:
        ti = TemplateInfo(app.path, template_name, cgi_id)
        # cache if in production mode
        if not settings.DEBUG:
            NO_TSELF_CACHE[key] = ti
    return [ ti ]


class TemplateInfo(object):
    '''
    Data class that holds information about a template's directories.  A TemplateInfo object
    is created by build_templateinfo_chain for each level in the Mako template inheritance chain.
    This object is then attached to the template object, which Mako already caches.
    That way we only do this work once per server run (in production mode).

    The app_dir is the search location for the styles/ and scripts/ folders, relative to the
    project base directory.  For typical apps, this is simply the app name.

    The template_name is the filename of the template.

    The cgi_id parameter is described in the MakoTemplateRenderer class below.
    '''
    def __init__(self, app_dir, template_name, cgi_id=None):
        # calculate directory and static url locations
        self.template_name = os.path.splitext(template_name)[0]  # remove its extension
        self.app_dir = app_dir
        app_reldir = os.path.relpath(self.app_dir, settings.BASE_DIR)
        self.app_url = posixpath.join(*app_reldir.split(os.path.sep))  # ensure we have forward slashes (even on windwos) because this is for urls

        # set up the filenames
        css_file = os.path.join(self.app_dir, 'styles', '%s.css' % self.template_name)
        cssm_file = os.path.join(self.app_dir, 'styles', '%s.cssm' % self.template_name)
        js_file = os.path.join(self.app_dir, 'scripts', '%s.js' % self.template_name)
        jsm_file = os.path.join(self.app_dir, 'scripts', '%s.jsm' % self.template_name)

        # the SASS templatename.scss (compile any updated templatename.scss files to templatename.css files)
        if DMP_OPTIONS.get('RUNTIME_SCSS_ENABLED'):
            check_template_scss(os.path.join(self.app_dir, 'styles'), self.template_name)

        # I want short try blocks, so there are several - for example, the first OSError can only occur for one reason: if the os.stat() fails.
        # I'm using os.stat here instead of os.path.exists because I need the st_mtime.  The os.stat checks that the file exists and gets the modified time in one command.

        # the static templatename.css file
        try:
            fstat = os.stat(css_file)
            self.css = '<link rel="stylesheet" type="text/css" href="%s?%s" />' % (posixpath.join(settings.STATIC_URL, self.app_url, 'styles', self.template_name + '.css'), cgi_id if cgi_id != None else int(fstat.st_mtime))
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
            self.js = '<script src="%s?%s"></script>' % (posixpath.join(settings.STATIC_URL, self.app_url, 'scripts', self.template_name + '.js'), cgi_id if cgi_id != None else int(fstat.st_mtime))
        except OSError:
            self.js = None

        # the mako-rendered templatename.jsm file
        try:
            fstat = os.stat(jsm_file)
            self.jsm = self.template_name + '.jsm'
        except OSError:
            self.jsm = None


    def append_css(self, request, context, html):
        '''Appends the CSS for this template's .css and .cssm files, if they exist, to the html list.'''
        # do we have a css?
        if self.css:
            html.append(self.css)  # the <link> was already created once in the constructor
        # do we have a cssm?
        if self.cssm:
            # engine.py already caches these loaders, so no need to cache them again here
            lookup = get_dmp_instance().get_template_loader_for_path(os.path.join(self.app_dir, 'styles'))
            css_text = lookup.get_template(self.cssm).render(request=request, context=context)
            if DMP_OPTIONS.get('RUNTIME_CSSMIN'):
                css_text = DMP_OPTIONS['RUNTIME_CSSMIN'](css_text)
            html.append('<style type="text/css">%s</style>' % css_text)


    def append_js(self, request, context, html):
        '''Appends the Javascript for this template's .js and .jsm files, if they exist to the html list.'''
        # do we have a js?
        if self.js:
            html.append(self.js)  # the <script> was already created once in the constructor
        # do we have a jsm?
        if self.jsm:
            # engine.py already caches these loaders, so no need to cache them again here
            lookup = get_dmp_instance().get_template_loader_for_path(os.path.join(self.app_dir, 'scripts'))
            js_text = lookup.get_template(self.jsm).render(request=request, context=context)
            if DMP_OPTIONS.get('RUNTIME_JSMIN'):
                js_text = DMP_OPTIONS['RUNTIME_JSMIN'](js_text)
            html.append('<script>%s</script>' % js_text)




#######################################################################
###   Utility functions

def _create_empty_mako_context(template):
    '''
    A small utility function that generates a Mako Context, used to
    get the inheritance for a template in build_templateinfo_chain()  above.
    This is only used when app and template_name are used.

    I'm hacking into the Mako private functions because I don't see a better way
    to get template inheritance.  This utility function at least contains it in
    one place.
    '''
    context = mako.runtime.Context(io.BytesIO())
    context._set_with_template(template)
    func, lclcontext = mako.runtime._populate_self_namespace(context, template)
    return lclcontext


