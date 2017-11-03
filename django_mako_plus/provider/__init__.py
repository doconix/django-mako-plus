from django.apps import apps
from django.template import Context

import mako.runtime

from ..util import get_dmp_instance
from ..uid import wuid
from .templateinfo import build_templateinfo_chain

import io
import warnings




############################################################
###  Public items in the package

from .base import init_providers, BaseProvider
from .compile import CompileProvider, CompileScssProvider, CompileLessProvider
from .links import LinkProvider, CssLinkProvider, JsLinkProvider, jscontext
from .mako_static import MakoCssProvider, MakoJsProvider

#########################################################
###  Primary functions

def links(tself, version_id=None, group=None):
    '''
    Returns the HTML for the given provider group.
    
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

    The optional version_id parameter is to overcome browser caches.  On some browsers,
    changes to your CSS/JS files don't get downloaded because the browser waits a time
    to check for a new version.  This wait time is set by your web server,
    and it's normally a good thing to speed everything up.  However,
    when you upload new CSS/JS files, you want all browsers to download the new
    files even if their cached versions have't expired yet.
    By adding an arbitrary id to the end of the .css and .js files, browsers will
    see the files as *new* anytime that id changes.  The default method
    for calculating the id is the file modification time (minutes since 1970).
    '''
    request = tself.context.get('request')
    provider_run = ProviderRun(request, tself.context, group, build_templateinfo_chain(tself, version_id))
    return provider_run.get_content()


class ProviderRun(object):
    '''Information for a run through a chain of template info objects and providers on each one.'''
    def __init__(self, request, context, group, chain):
        self.uid = wuid()       # a unique Id for this run
        self.request = request  # request from the render call
        self.context = context  # context from the render call
        self.group = group      # the provider group being rendered (usually None)
        self.chain = chain      # list of TemplateInfos matching the template inheritance
        self.chain_index = 0    # current index of the inheritance chain as the run goes
        
    def get_content(self):
        '''Loops each TemplateInfo providers list, returning the combined content.'''
        self.chain_index = 0
        self.html = []
        for ti in self.chain:
            for provider_i, provider in enumerate(ti.providers):
                if self.group is None or provider.group == self.group:
                    content = provider.get_content(self)
                    if content:
                        self.html.append(content)
            self.chain_index += 1
        return '\n'.join(self.html)



def template_links(request, app, template_name, context=None, version_id=None, group=None, force=True):
    '''
    Returns the HTML for the given provider group, using an app and template name.
    This method should not normally be used (use links() instead).  The use of 
    this method is when provider need to be called from regular python code instead
    of from within a rendering template environment.
    
    See links() for documentation on the variables.
    '''
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
    return links(mako_context['self'], version_id=version_id, group=group)




#######################################################################
###   Deprecated methods - these are deprecated as of Oct 2017

def link_css(tself, version_id=None):
    '''
    Deprecated as of Oct 2017.
    Use `django_mako_plus.links(self, 'styles')` instead.
    '''
    warnings.warn("link_css() is deprecated as of Oct 2017.  Use `django_mako_plus.links(self, 'styles')` instead.", DeprecationWarning)
    return links(tself, version_id=version_id, group='styles')


def link_js(tself, version_id=None):
    '''
    Deprecated as of Oct 2017.
    Use `django_mako_plus.links(self, 'scripts')` instead.
    '''
    warnings.warn("link_js() is deprecated as of Oct 2017.  Use `django_mako_plus.links(self, 'scripts')` instead.", DeprecationWarning)
    return links(tself, version_id=version_id, group='scripts')


def link_template_css(request, app, template_name, context, version_id=None, force=True):
    '''
    Deprecated as of Oct 2017.
    Use `django_mako_plus.template_links(..., group='styles')` instead.
    '''
    warnings.warn("link_template_css() is deprecated as of Oct 2017.  Use `django_mako_plus.template_links(..., group='styles')` instead.", DeprecationWarning)
    return template_links(request, app, template_name, context, version_id=version_id, group='styles', force=force)


def link_template_js(request, app, template_name, context, version_id=None, force=True):
    '''
    Deprecated as of Oct 2017.
    Use `django_mako_plus.template_links(..., group='scripts')` instead.
    '''
    warnings.warn("link_template_js() is deprecated as of Oct 2017.  Use `django_mako_plus.template_links(..., group='scripts')` instead.", DeprecationWarning)
    return template_links(request, app, template_name, context, version_id=version_id, group='scripts', force=force)


