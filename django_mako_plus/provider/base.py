from django.utils.encoding import force_text
from django.conf import settings

from ..util import merge_dicts

import os
import os.path



##############################################################
###   Static File Providers

class BaseProvider(object):
    '''
    A list of provider instances is attached to each template in the system.
    During a provider run, all provider lists are run.

        base.htm      [ JsLinkProvider1, CssLinkProvider1, ... ]
           |
        app_base.htm  [ JsLinkProvider2, CssLinkProvider2, ... ]
           |
        index.html    [ JsLinkProvider3, CssLinkProvider3, ... ]

    The data argument sent into provide() spans a run vertically, meaning
    the three JsLinkProviders above share the same data dict.
    '''

    default_options = {
        'group': 'styles',
        'enabled': True,
    }

    def __init__(self, app_config, template_file, options):
        self.app_config = app_config
        self.subdir, self.template_file = os.path.split(template_file)
        self.subdir_parts = os.path.normpath(self.subdir).split(os.path.sep)
        self.template_name, _ = os.path.splitext(self.template_file)
        self.options = merge_dicts(self.default_options, options)     # combined options dictionary

    @property
    def group(self):
        return self.options['group']

    def start(self, provider_run, data):
        '''
        Called on the *main* template's provider list as the run starts.
        Initialize values in the data dictionary here.
        '''
        pass

    def provide(self, provider_run, data):
        '''Called on *each* template's provider list in the chain - use provider_run.write() for content'''
        pass

    def finish(self, provider_run, data):
        '''
        Called on the *main* template's provider list as the run finishes
        Finalize values in the data dictionary here.
        '''
        pass



