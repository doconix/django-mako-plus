from django.apps import apps
from django.conf import settings
from django.template import Context

import mako.runtime

from ..util import get_dmp_instance
from ..util import DMP_OPTIONS, split_app
from ..uid import wuid

import io
import warnings




############################################################
###  Public items in the package

from .base import init_providers, BaseProvider
from .compile import CompileProvider, CompileScssProvider, CompileLessProvider
from .links import LinkProvider, CssLinkProvider, JsLinkProvider, JsContextProvider, jscontext


# key to attach Provider objects to Mako Template objects during producting mode.
# I attach it to template objects because templates are already cached by mako, so
# caching them here would result in double-caching.
PROVIDERS_KEY = '_django_mako_plus_providers_'


#########################################################
###  Primary functions

def links(tself, version_id=None, group=None):
    '''Returns the HTML for the given provider group (or all groups if None)'''
    request = tself.context.get('request')
    provider_run = ProviderRun(tself, version_id, group)
    provider_run.get_content()
    return provider_run.get_content()


class ProviderRun(object):
    '''A run through a template inheritance'''
    def __init__(self, tself, version_id=None, group=None):
        self.uid = wuid()                           # a unique id for this run
        self.template = tself.template              # the template object
        self.request = tself.context.get('request') # request from the render()
        self.context = tself.context                # context from the render()
        self.group = group                          # the provider group being rendered (usually None)
        self.version_id = version_id                # unique number for overriding the cache (see LinkProvider)
        self._buffer = None                         # html to send back to the browser (providers add to this)
        # provider data is separate from provider objects because a template (and its providers) can be in many chains at once,
        # such as base.htm's providers being in almost every chain on the site. this makes it unique to each provider on this run.
        self.provider_data = [ {} for i in range(len(DMP_OPTIONS['RUNTIME_PROVIDER_FACTS'])) ]
        # discover the ancestor templates for this template `self`
        self.chain = []
        self.chain_index = 0
        # a set of providers for each template
        while tself is not None:
            # check if already attached to template, create if necessary
            providers = getattr(tself.template, PROVIDERS_KEY, None)
            if providers is None:
                app_config, template_path = split_app(tself.template.filename)
                providers = [ pf.create(app_config, template_path, i) for i, pf in enumerate(DMP_OPTIONS['RUNTIME_PROVIDER_FACTS']) ]
                if not settings.DEBUG: # attach to template for speed in production mode
                    setattr(tself.template, PROVIDERS_KEY, providers)
            self.chain.append(providers)
            # loop with the next inherited template
            tself = tself.inherits
        # we need furthest ancestor first, current template last so current template (such as CSS) can override ancestors
        self.chain.reverse()

    def get_content(self):
        '''Runs the providers for each template in the current inheritance chain, returning the combined content.'''
        self._buffer = io.StringIO()
        self.chain_index = -1
        for providers in self.chain:
            self.chain_index += 1
            for provider, data in zip(providers, self.provider_data):
                if self.group is None or provider.group == self.group:
                    provider.provide(self, data)
        return self._buffer.getvalue()

    def write(self, content):
        self._buffer.write(content)
        if settings.DEBUG:
            self._buffer.write('\n')


def template_links(request, app, template_name, context=None, version_id=None, group=None, force=True):
    '''
    Returns the HTML for the given provider group, using an app and template name.
    This method should not normally be used (use links() instead).  The use of
    this method is when provider need to be called from regular python code instead
    of from within a rendering template environment.
    '''
    if isinstance(app, str):
        app = apps.get_app_config(app)
    if context is None:
        context = {}
    template_obj = get_dmp_instance().get_template_loader(app, create=True).get_mako_template(template_name, force=force)
    return template_obj_links(request, template_obj, context, version_id, group)


def template_obj_links(request, template_obj, context=None, version_id=None, group=None):
    '''
    Returns the HTML for the given provider group, using a template object.
    This method should not normally be used (use links() instead).  The use of
    this method is when provider need to be called from regular python code instead
    of from within a rendering template environment.
    '''
    # the template_obj can be a MakoTemplateAdapter or a Mako Template
    # if our DMP-defined MakoTemplateAdapter, switch to the embedded Mako Template
    template_obj = getattr(template_obj, 'mako_template', template_obj)
    # create a mako context so it seems like we are inside a render
    # I'm hacking into private Mako methods here, but I can't see another
    # way to do this.  Hopefully this can be rectified at some point.
    context_dict = {
        'request': request,
    }
    if isinstance(context, Context):
        for d in context:
            context_dict.update(d)
    elif context is not None:
        context_dict.update(context)
    context_dict.pop('self', None)  # some contexts have self in them, and it messes up render_unicode below because we get two selfs
    runtime_context = mako.runtime.Context(io.BytesIO(), **context_dict)
    runtime_context._set_with_template(template_obj)
    _, mako_context = mako.runtime._populate_self_namespace(runtime_context, template_obj)
    return links(mako_context['self'], version_id=version_id, group=group)




