# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1492747574.045729
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/programming/django-mako-plus/testing_app/templates/base.htm'
_template_uri = 'base.htm'
_source_encoding = 'utf-8'
import django_mako_plus
import os, os.path, re, json
_exports = ['content']


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        self = context.get('self', UNDEFINED)
        def content():
            return render_content(context._locals(__M_locals))
        __M_writer = context.writer()
        __M_writer('<!DOCTYPE html>\n<html>\n    <meta charset="UTF-8">\n    <head>\n\n        <title>Testing_App</title>\n\n')
        __M_writer('        ')
        __M_writer(str( django_mako_plus.link_css(self) ))
        __M_writer('\n\n    </head>\n    <body>\n        ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'content'):
            context['self'].content(**pageargs)
        

        __M_writer('\n\n')
        __M_writer('        ')
        __M_writer(str( django_mako_plus.link_js(self) ))
        __M_writer('\n\n    </body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def content():
            return render_content(context)
        __M_writer = context.writer()
        __M_writer('\n        ')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "filename": "/Users/conan/Documents/data/programming/django-mako-plus/testing_app/templates/base.htm", "line_map": {"34": 14, "35": 17, "36": 17, "37": 17, "43": 13, "49": 13, "18": 0, "55": 49, "26": 1, "27": 9, "28": 9, "29": 9}, "uri": "base.htm"}
__M_END_METADATA
"""
