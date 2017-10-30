from django.conf import settings

from ..util import DMP_OPTIONS

import os
import os.path

# key to attach TemplateInfo objects and static renderer to the Mako Template itself
# I attach it to the template objects because they are already cached by mako, so
# caching them again here would result in double-caching.  It's a bit of a
# monkey-patch to set them as attributes in the Mako templates, but it's efficient
# and encapsulated entirely within this file
DMP_TEMPLATEINFO_KEY = '_django_mako_plus_templateinfo'



###################################################
###  TemplateInfo: attached to each template

class TemplateInfo(object):
    '''
    Data class that holds information about a template's directories.  A TemplateInfo object
    is created by _build_templateinfo_chain for each level in the Mako template inheritance chain.
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
        for provider_class in DMP_OPTIONS['RUNTIME_STATIC']:
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




def build_templateinfo_chain(tself, cgi_id=None):
    '''
    Retrieves a chain of TemplateInfo objects.  The chain is formed by following
    template inheritance through inherit tags: <%inherit file="base_homepage.htm" />

    For efficiency, the templates are ordered with the specialization template first.
    The returned list should usually be reversed() by the calling code to put the
    superclass CSS/JS first (allowing the specialization to override supertemplate styles
    and scripts).
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

    
    
