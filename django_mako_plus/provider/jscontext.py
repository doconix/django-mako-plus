from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from ..util import merge_dicts
from .base import BaseProvider

import json



class JsContextProvider(BaseProvider):
    '''Adds context variables to the JS environment within a page'''
    default_options = merge_dicts(BaseProvider.default_options, {  
        'group': 'scripts',
        'weight': 5,  # higher than JsLinkProvider so the JS has the variables already in memory
    })
    
    def get_content(self, provider_run):
        # we only have to add the JS once for each template render (not once for each inherited template)
        # since the loop goes from furthest ancestor to the current template, we send the JS just before
        # the furthest ancestor (inheritance index 0)
        if provider_run.inheritance_index == 0:
            js_context = { k: provider_run.context[k] for k in provider_run.context.kwargs if isinstance(k, jscontext) }
            if len(js_context) > 0:
                return '<script>window.context = {};</script>'.format(json.dumps(js_context, cls=DjangoJSONEncoder))
        return None
        
        

class jscontext(str):
    '''
    Marks a key in the context dictionary as a JS context item.
    JS context items are sent to the template like normal,
    but they are also added to the runtime JS namespace.
    
    In myview.py:
        from django_mako_plus import js_context, view_function
        
        @view_function
        def myview(request):
            context = {
                jscontext('age'): 50,
                jscontext('name'): 'Homer Simpson',
                'another': 'sent only to template',
            }
            return request.dmp_render('myview.html', context)
    
    In myview.html:
        ${ django_mako_plus.providers('scripts')
    Output in template:
        var context = {
            "age": 50,
            "name": "Homer Simpson"
        };
    
    In myview.js:
        console.log(context.age);
    '''
    # no code needed, just using the class for identity
    pass
    
    
