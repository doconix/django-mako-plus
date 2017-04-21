# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1486653837.554612
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/teaching/2017/IS 411-413/fomoproject/homepage/styles/index.cssm'
_template_uri = 'index.cssm'
_source_encoding = 'utf-8'
import django_mako_plus
import os, os.path, re, json
_exports = []


import random 

def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        __M_writer('\n\n.content h3 {\n    font-size: ')
        __M_writer(str( random.randint(50, 100) ))
        __M_writer('px;\n}')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "/Users/conan/Documents/data/teaching/2017/IS 411-413/fomoproject/homepage/styles/index.cssm", "uri": "index.cssm", "source_encoding": "utf-8", "line_map": {"18": 1, "20": 0, "25": 1, "26": 4, "27": 4, "33": 27}}
__M_END_METADATA
"""
