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
    '''
    DEFAULT_OPTIONS = {
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'scripts',
        # the encoder to use for the JSON structure
        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoder = import_string(self.options['encoder'])
        if log.isEnabledFor(logging.DEBUG):
            log.debug('%s created', repr(self))

    def provide(self):
        # we output on the first run through - the context is only needed once
        if not self.is_first():
            return

        # generate the context dictionary
        data = {
            'id': self.provider_run.uid,
            'version': __version__,
            'templates': [ '{}/{}'.format(p.app_config.name, p.template_relpath) for p in self.iter_related() ],
            'app': self.provider_run.request.dmp.app if self.provider_run.request is not None else None,
            'page': self.provider_run.request.dmp.page if self.provider_run.request is not None else None,
            'log': log.isEnabledFor(logging.DEBUG),
            'values': {
                'id': self.provider_run.uid,
            },
        }
        for k in self.provider_run.context.keys():
            if isinstance(k, jscontext):
                value = self.provider_run.context[k]
                data['values'][k] = value.__jscontext__() if callable(getattr(value, '__jscontext__', None)) else value

        # output the script
        self.write('<script>')
        self.write('DMP_CONTEXT.set({data});'.format(
            data=json.dumps(data, cls=self.encoder, separators=(',', ':'))
        ))
        self.write('</script>')


class jscontext(str):
    '''
    Marks a key in the context dictionary as a JS context item.
    JS context items are sent to the template like normal,
    but they are also added to the runtime JS namespace.

    See the tutorial for more information on this function.
    '''
    # no code needed, just using the class for identity
