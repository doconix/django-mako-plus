from django.utils.encoding import force_text
from django.conf import settings

from ..util import merge_dicts

import os
import os.path



##############################################################
###   Static File Providers

class BaseProvider(object):
    '''
    Abstract base provider class.  An instance is tied to a template at runtime.
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
