from django.conf import settings
from django.apps import apps
from django.template import TemplateDoesNotExist, Context, RequestContext

from mako.exceptions import MakoException
from mako.template import Template as MakoTemplate
from mako.lookup import TemplateLookup as MakoTemplateLookup
import mako.runtime

from .sass import check_template_scss
from .util import get_dmp_instance, log, DMP_OPTIONS

import os, os.path, io, posixpath
from collections import deque
import glob, warnings


# a lookup object to cache 
forced_lookup = MakoTemplateLookup()



def get_static(tself, group=None, cgi_id=None, duplicates=True):
    '''
    Returns the HTML for the given static files group.
    
        Add this at the top (<head> section) of your template:
        ${ django_mako_plus.static_group(self, 'styles') }
    
        Add this at the bottom of your template:
        ${ django_mako_plus.static_group(self, 'scripts') }
    
        Or, to get all content in one call:
        ${ django_mako_plus.static_group(self) }

    Suppose you have two html files connected via template inheritance: index.html
    and base.htm.  This method will render the links for all static files
    with the names of either of these two templates.  Assuming the default
    providers are listed in settings.py, up to four files are linked/sourced:

        base.htm       Generates a <style> link for app/styles/base.css
            |          and a <style> source for app/styles/base.cssm
            |
        index.html     Generates a <style> link for app/styles/index.css
                       and a <style> source for app/styles/index.cssm

    This call must be made from within a rendering Mako template because
    this is where you have access to the "self" namespace.
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
    request = tself.context.get('request')
    for ti in reversed(build_templateinfo_chain(tself, cgi_id)):
        ti.append_static(request, tself.context, html, group=group, duplicates=duplicates)
    return '\n'.join(html)



def get_template_static(request, app, template_name, context=None, group=None, cgi_id=None, force=True, duplicates=True):
    if isinstance(app, str):
        app = apps.get_app_config(app)
    if context is None:
        context = {}

    # get the template object normally
    template = get_dmp_instance().get_template_loader(app, create=True).get_mako_template(template_name, force=force)
        
    # create a mako context so it seems like we are inside a render
    # I'm hacking into private Mako methods here, but I can't see another
    # way to do this.  Hopefully this can be rectified at some point.
    context_dict = {}
    if isinstance(context, Context):
        for d in context:
            context_dict.update(d)
    elif context is not None:
        context_dict.update(context)
    context_dict.pop('self', None)  # some contexts have self in them, and it messes up render_unicode below because we get two selfs
    runtime_context = mako.runtime.Context(io.BytesIO(), **context_dict)
    runtime_context._set_with_template(template)
    _, mako_context = mako.runtime._populate_self_namespace(runtime_context, template)
    return get_static(mako_context['self'], group=group, cgi_id=cgi_id, duplicates=duplicates)

    
    
###################################################
###  TemplateInfo: attached to each template

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
        self.app_dir = app_dir
        self.template_name = template_name
        
        # initialize the static providers
        self.providers = []
        for provider_class in DMP_OPTIONS['RUNTIME_STATIC_PROVIDERS']:
            self.providers.append(provider_class(app_dir, template_name, cgi_id))


    def append_static(self, request, context, html, group=None, duplicates=True):
        if request is None:
            provider_keys = set() 
        else:
            if not hasattr(request, '_dmp_static_provider_keys'):
                setattr(request, '_dmp_static_provider_keys', set())
            provider_keys = request._dmp_static_provider_keys
        for provider in self.providers:
            provider_key = ( self.app_dir, self.template_name, provider.__class__.__qualname__ )
            if (duplicates or provider_key not in provider_keys) and \
               (group is None or provider.group == group):
                    provider.append_static(request, context, html)
                    provider_keys.add(provider_key)


##############################################################
###   Default providers - one of these exists for each
###   static file pattern: *.css, *.cssm, *.js, *.jsm, etc.

class BaseProvider(object):
    '''
    A list of providers is attached to each template as it is process.
    These are cached with the template, so .__init__() is only called once
    per system runtime, while .append_static() is called for each
    request.  Optimize the methods accordingly.
    '''
    default = False
    group = 'group name here'
    weight = 0  # higher weights sort first and thus process before others
    def __init__(self, app_dir, template_name, cgi_id):
        self.app_dir = app_dir
        self.template_name = os.path.splitext(template_name)[0]  # remove its extension
        self.cgi_id = cgi_id
        self.init()

    def init(self):
        pass
        
    def append_static(self, request, context, html):
        pass
        

class CssProvider(BaseProvider):
    '''Provides the link for *.css files'''
    group = 'styles'
    def init(self):
        pattern = os.path.join(self.app_dir, os.path.join('styles', self.template_name + '.css'))
        content_builder = []
        for fullpath in glob.glob(pattern):
            if self.cgi_id is None:
                self.cgi_id = int(os.stat(fullpath).st_mtime)
            href = posixpath.join(settings.STATIC_URL, os.path.relpath(fullpath, settings.BASE_DIR))  # ensure we have forward slashes (even on windows) because this is for urls
            content_builder.append('<link rel="stylesheet" type="text/css" href="{}?{}" />'.format(href, self.cgi_id))
        self.content = '\n'.join(content_builder)
        
    def append_static(self, request, context, html):
        html.append(self.content)


class CompileScssProvider(BaseProvider):
    '''Compiles *.scss files to *.css files when needed.'''
    weight = 10  # so sass compiles it before the CssProvider runs
    def init(self):
        # doing the check in init() so it only happens one time during production
        check_template_scss(os.path.join(self.app_dir, 'styles'), self.template_name, 'css')
        
    
class MakoCssProvider(BaseProvider):
    '''Provides the content for *.cssm files'''
    group = 'styles'
    def init(self):
        self.cssm_dir = os.path.join(self.app_dir, 'styles')
        try:
            self.template = get_dmp_instance().get_template_loader_for_path(self.cssm_dir).get_template(self.template_name + '.cssm')
        except TemplateDoesNotExist:
            self.template = None
        
    def append_static(self, request, context, html):
        if self.template is not None:
            content = self.template.render(request=request, context=context)
            if DMP_OPTIONS.get('RUNTIME_CSSMIN') is not None:
                content = DMP_OPTIONS['RUNTIME_CSSMIN'](content)
            html.append('<style type="text/css">{}</style>'.format(content))
        

class CompileMakoScssProvider(BaseProvider):
    '''Compiles *.scssm files to *.cssm files when needed.'''
    weight = 10  # so sass compiles it before the MakoCssProvider runs
    def init(self):
        # doing the check in init() so it only happens one time during production
        check_template_scss(os.path.join(self.app_dir, 'styles'), self.template_name, 'cssm')
        
    
class JsProvider(BaseProvider):
    '''Provides the link for *.js files'''
    group = 'scripts'
    def init(self):
        pattern = os.path.join(self.app_dir, os.path.join('scripts', self.template_name + '.js'))
        content_builder = []
        for fullpath in glob.glob(pattern):
            if self.cgi_id is None:
                self.cgi_id = int(os.stat(fullpath).st_mtime)
            href = posixpath.join(settings.STATIC_URL, os.path.relpath(fullpath, settings.BASE_DIR))  # ensure we have forward slashes (even on windows) because this is for urls
            content_builder.append('<script src="{}?{}"></script>'.format(href, self.cgi_id))
        self.content = '\n'.join(content_builder)
        
    def append_static(self, request, context, html):
        html.append(self.content)


class MakoJsProvider(BaseProvider):
    '''Provides the content for *.jsm files'''
    group = 'scripts'
    def init(self):
        self.cssm_dir = os.path.join(self.app_dir, 'scripts')
        try:
            self.template = get_dmp_instance().get_template_loader_for_path(self.cssm_dir).get_template(self.template_name + '.jsm')
        except TemplateDoesNotExist:
            self.template = None
        
    def append_static(self, request, context, html):
        if self.template is not None:
            content = self.template.render(request=request, context=context)
            if DMP_OPTIONS.get('RUNTIME_JSMIN') is not None:
                content = DMP_OPTIONS['RUNTIME_JSMIN'](content)
            html.append('<script type="text/javascript">{}</script>'.format(content))




##############################################################################
###   Builds a chain of TemplateInfo objects, one for each template
###   in the inheritance chain of a given template.

# key to attach TemplateInfo objects and static renderer to the Mako Template itself
# I attach it to the template objects because they are already cached by mako, so
# caching them again here would result in double-caching.  It's a bit of a
# monkey-patch to set them as attributes in the Mako templates, but it's efficient
# and encapsulated entirely within this file
DMP_TEMPLATEINFO_KEY = '_django_mako_plus_templateinfo'

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
    # step through the template inheritance
    chain = []
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


#######################################################################
###   Deprecated methods - these are deprecated as of Oct 2017

def link_css(tself, cgi_id=None, duplicates=True):
    '''
    Deprecated as of Oct 2017.
    Use `django_mako_plus.get_static(self, 'styles')` instead.
    '''
    warnings.warn("link_css() is deprecated as of Oct 2017.  Use `django_mako_plus.get_static(self, 'styles')` instead.", DeprecationWarning)
    return get_static(tself, group='styles', cgi_id=cgi_id, duplicates=duplicates)


def link_js(tself, cgi_id=None, duplicates=True):
    '''
    Deprecated as of Oct 2017.
    Use `django_mako_plus.get_static(self, 'scripts')` instead.
    '''
    warnings.warn("link_js() is deprecated as of Oct 2017.  Use `django_mako_plus.get_static(self, 'scripts')` instead.", DeprecationWarning)
    return get_static(tself, group='scripts', cgi_id=cgi_id, duplicates=duplicates)


def link_template_css(request, app, template_name, context, cgi_id=None, force=True, duplicates=True):
    '''
    Deprecated as of Oct 2017.
    Use `django_mako_plus.get_template_static(..., group='styles')` instead.
    '''
    warnings.warn("link_template_css() is deprecated as of Oct 2017.  Use `django_mako_plus.get_template_static(..., group='styles')` instead.", DeprecationWarning)
    return get_template_static(request, app, template_name, context, group='styles', cgi_id=cgi_id, force=force, duplicates=duplicates)


def link_template_js(request, app, template_name, context, cgi_id=None, force=True, duplicates=True):
    '''
    Deprecated as of Oct 2017.
    Use `django_mako_plus.get_template_static(..., group='scripts')` instead.
    '''
    warnings.warn("link_template_js() is deprecated as of Oct 2017.  Use `django_mako_plus.get_template_static(..., group='scripts')` instead.", DeprecationWarning)
    return get_template_static(request, app, template_name, context, group='scripts', cgi_id=cgi_id, force=force, duplicates=duplicates)


