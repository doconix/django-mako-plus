from django.utils.module_loading import import_string
import json
import logging
from ..version import __version__
from ..util import log
from .base import BaseProvider

###################################
###  JS Context Provider

class JsContextProvider(BaseProvider):
    '''
    Adds all js_context() variables to DMP_CONTEXT.
    This should be listed before JsLinkProvider so the
    context variables are available during <script> runs.
    '''
    DEFAULT_OPTIONS = {
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'scripts',
        # the encoder to use for the JSON structure
        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
    }

    def __init__(self, template, options):
        super().__init__(template, options)
        self.encoder = import_string(self.options['encoder'])
        self.template = "{}/{}".format(self.app_config.name, self.template_relpath)
        if log.isEnabledFor(logging.DEBUG):
            log.debug('%s created', repr(self))

    def start(self, provider_run, data):
        data['templates'] = []

    def provide(self, provider_run, data):
        data['templates'].append(self.template)

    def finish(self, provider_run, data):
        if len(data['templates']) == 0:
            return
        context_data = {
            jscontext('__router__'): {
                'template': self.template,
                'app': provider_run.request.dmp.app if provider_run.request is not None else None,
                'page': provider_run.request.dmp.page if provider_run.request is not None else None,
                'log': log.isEnabledFor(logging.DEBUG),
            },
        }
        for k in provider_run.context.keys():
            if isinstance(k, jscontext):
                value = provider_run.context[k]
                context_data[k] = value.__jscontext__() if hasattr(value, '__jscontext__') else value
        # add to the JS DMP_CONTEXT
        provider_run.write('<script>')
        provider_run.write('DMP_CONTEXT.set("{version}", "{contextid}", {data}, {templates});'.format(
            version=__version__,
            contextid=provider_run.uid,
            data=json.dumps(context_data, cls=self.encoder, separators=(',', ':')) if context_data else '{}',
            templates=json.dumps(data['templates']),
        ))
        provider_run.write('</script>')


class jscontext(str):
    '''
    Marks a key in the context dictionary as a JS context item.
    JS context items are sent to the template like normal,
    but they are also added to the runtime JS namespace.

    See the tutorial for more information on this function.
    '''
    # no code needed, just using the class for identity
