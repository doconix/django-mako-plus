from django.apps import apps
from django.template import Context

import mako.runtime

from ..util import get_dmp_instance
from .templateinfo import build_templateinfo_chain

import io
import warnings



# used when not specified in settings.py
DEFAULT_STATIC_FILE_PROVIDERS = [
    { 'provider': 'django_mako_plus.CssLinkProvider' },
    { 'provider': 'django_mako_plus.JsLinkProvider'  },
]


############################################################
###  Public items in the package

from .provider_base import init_providers, BaseProvider
from .provider_compile import CompileProvider, CompileScssProvider, CompileLessProvider
from .provider_links import LinkProvider, CssLinkProvider, JsLinkProvider
from .provider_mako import MakoCssProvider, MakoJsProvider


#########################################################
###  Primary functions

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


