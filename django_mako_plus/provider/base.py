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
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'styles',
        # whether enabled (see "Dev vs. Prod" in the DMP docs)
        'enabled': True,
    }

    def __init__(self, app_config, template_file, options):
        '''
        Creates the provider.

        When settings.DEBUG=True, the provider is recreated per request.
        When settings.DEBUG=False, this constructor is run only once per server run.

        The fields created here deconstruct the location of the template.  Examples:

        Regular location: /homepage/templates/index.html
            self.app_config:            AppConfig for "homepage"
            self.app_config.path:       "/absolute/path/to/homepage/"
            self.template_file:         "index.html"
            self.template_subdir:       ""
            self.template_name:         "index"
            self.template_ext:          ".html"
            self.template:              "index"                          # name within "homepage/templates/"

        Subdir location: /homepage/templates/mail/signup/welcome.txt
            self.app_config:            AppConfig for "homepage"
            self.app_config.path:       "/absolute/path/to/homepage/"
            self.template_file:         "welcome.txt"
            self.template_subdir:       "mail/signup"
            self.template_name:         "welcome"
            self.template_ext:          ".txt"
            self.template:              "mail/signup/welcome"            # name within "homepage/templates/"
        '''
        self.app_config = app_config
        subdir, self.template_file = os.path.split(template_file)
        self.template_name, self.template_ext = os.path.splitext(self.template_file)
        subdir_parts = os.path.normpath(subdir).split(os.path.sep)
        if len(subdir_parts) > 1:
            self.template_subdir = os.path.join(*subdir_parts[1:])
            self.template = os.path.join(self.template_subdir, self.template_name)
        else:
            self.template_subdir = ""
            self.template = self.template_name
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
