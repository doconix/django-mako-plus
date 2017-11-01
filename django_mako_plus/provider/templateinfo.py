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
    '''
    def __init__(self, app_dir, template_name, version_id):
        self.app_dir = app_dir              # absolute path
        self.template_name = template_name  # without the extension
        self.providers = [ pf.create(app_dir, template_name, version_id) for pf in DMP_OPTIONS['RUNTIME_PROVIDERS'] ]


def build_templateinfo_chain(tself, version_id):
    '''
    Retrieves a chain of TemplateInfo objects.  The chain is formed by following
    template inheritance through inherit tags: <%inherit file="parent.htm" />.
    '''
    # step through the template inheritance
    chain = []
    while tself is not None:
        # first check the cache, creating if necessary
        ti = getattr(tself.template, DMP_TEMPLATEINFO_KEY, None)
        if ti is None:
            template_dir, template_name = os.path.split(tself.template.filename)
            app_dir = os.path.dirname(template_dir)
            ti = TemplateInfo(app_dir, template_name, version_id)
            # cache in template if in production mode
            if not settings.DEBUG:
                setattr(tself.template, DMP_TEMPLATEINFO_KEY, ti)
        # append the TemplateInfo
        chain.append(ti)
        # loop with the next inherited template
        tself = tself.inherits

    # return
    chain.reverse() # we need furthest ancestor first, current template last
    return chain

    
    
