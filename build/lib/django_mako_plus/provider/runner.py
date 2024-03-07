from django.apps import apps
from django.conf import settings
from django.utils.module_loading import import_string
from collections import namedtuple
import io
import inspect
from uuid import uuid1
from ..template import template_inheritance
from ..util import qualified_name, b58enc



# __init__() below creates a list of templates, each of which has a list of providers
# this named tuple adds a small amount of extra clarity to it.
# I could use a dict or OrderedDict, but I need order AND fast indexing
TemplateProviderList = namedtuple("TemplateProviderList", [ 'template', 'providers' ])

# ProviderRun.initialize_providers() creates a list of these to hold provider options from settings.py
# I can't keep the options inside the provider class itself because a given class can be listed
# more than once in settings.py (with different options).
ProviderEntry = namedtuple("ProviderEntry", [ 'cls', 'options' ])



####################################################
###   Main runner for providers

class ProviderRun(object):
    '''A run through the providers for tself and its ancestors'''
    SETTINGS_KEY = 'CONTENT_PROVIDERS'
    CONTENT_PROVIDERS = []

    @classmethod
    def initialize_providers(cls):
        '''Initializes the providers (called from dmp app ready())'''
        dmp = apps.get_app_config('django_mako_plus')
        # regular content providers
        cls.CONTENT_PROVIDERS = []
        for provider_settings in dmp.options[cls.SETTINGS_KEY]:
            # import the class for this provider
            assert 'provider' in provider_settings, "Invalid entry in settings.py: CONTENT_PROVIDERS item must have 'provider' key"
            provider_cls = import_string(provider_settings['provider'])
            # combine options from all of its bases, then from settings.py
            options = {}
            for base in reversed(inspect.getmro(provider_cls)):
                options.update(getattr(base, 'DEFAULT_OPTIONS', {}))
            options.update(provider_settings)
            # add to the list
            if options['enabled']:
                pe = ProviderEntry(provider_cls, options)
                pe.options['template_cache_key'] = '_dmp_provider_{}_'.format(id(pe))
                cls.CONTENT_PROVIDERS.append(pe)


    def __init__(self, tself, group=None):
        '''
        tself:              `self` object from a Mako template (available during rendering).
        group:              provider group to include (defaults to all groups if None)
        '''
        # a unique context id for this run
        self.uid = b58enc(uuid1().int)
        self.tself = tself
        self.request = tself.context.get('request')
        self.context = tself.context
        self.buffer = io.StringIO()

        # get the ProviderClassInfo objects that are used in this group
        group_pes = [ pe for pe in self.CONTENT_PROVIDERS if group is None or pe.options['group'] == group ]

        # Create a map of template -> providers for this run
        #   {
        #       base.htm:      [ JsLinkProvider(), CssLinkProvider(), ... ]
        #       app_base.htm:  [ JsLinkProvider(), CssLinkProvider(), ... ]
        #       index.html:    [ JsLinkProvider(), CssLinkProvider(), ... ]
        #   }
        self.templates = []
        for tmpl in self._get_template_inheritance():
            tpl = TemplateProviderList(tmpl, [])
            for index, pe in enumerate(group_pes):
                tpl.providers.append(pe.cls(self, tmpl, index, pe.options))
            self.templates.append(tpl)

    def _get_template_inheritance(self):
        '''Returns a list of the template inheritance of tself, starting with the oldest ancestor'''
        return reversed(list(template_inheritance(self.tself)))

    def run(self):
        '''Performs the run through the templates and their providers'''
        for tpl in self.templates:
            for provider in tpl.providers:
                provider.provide()

    def write(self, content):
        '''Provider instances use this to write to the buffer'''
        self.buffer.write(content)
        if settings.DEBUG:
            self.buffer.write('\n')

    def getvalue(self):
        '''Returns the buffer string'''
        return self.buffer.getvalue()
