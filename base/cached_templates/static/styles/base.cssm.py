# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1382238031.996187
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/programming/django-mako/base/static/styles/base.cssm'
_template_uri = 'base.cssm'
_source_encoding = 'ascii'
import os, os.path, re
from calculator import models as cmod
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        range = context.get('range', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer('/* \n  Dynamic CSS for the base.html page goes here.  In other words, Python code can be placed here.\n  \n  Since base.html is the common ancestor of all templates of all apps on our site,\n  CSS included here will be placed on *every* page of the site.\n*/\n')
        # SOURCE LINE 7

  # just a silly example of embedding Python/Mako code within the .cssm file.
        import random
        font_color = ''.join([ random.choice('0123456789ABCDEF') for i in range(6) ])
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['i','random','font_color'] if __M_key in __M_locals_builtin_stored]))
        # SOURCE LINE 11
        __M_writer('\n\n#site_header {\n  font-size: 22px; \n  text-align: center; \n  color: #')
        # SOURCE LINE 16
        __M_writer(str( font_color ))
        __M_writer('; \n  padding-bottom: 6px; \n  border-bottom: 1px solid #004080;\n}\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


