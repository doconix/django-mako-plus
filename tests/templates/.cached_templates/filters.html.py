# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1492824694.038183
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/programming/django-mako-plus/tests/templates/filters.html'
_template_uri = 'filters.html'
_source_encoding = 'utf-8'
import django_mako_plus
import os, os.path, re, json
from django_mako_plus import django_syntax, jinja2_syntax, alternate_syntax
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def __M_anon_5():
            __M_caller = context.caller_stack._push_frame()
            try:
                context._push_buffer()
                __M_writer = context.writer()
                __M_writer('\n    {{ jinja2_var }}\n')
            finally:
                __M_buf, __M_writer = context._pop_buffer_and_writer()
                context.caller_stack._pop_frame()
            __M_writer(jinja2_syntax(local)(__M_buf.getvalue()))
            return ''
        def __M_anon_1():
            __M_caller = context.caller_stack._push_frame()
            try:
                context._push_buffer()
                __M_writer = context.writer()
                __M_writer('\n    {{ django_var }}\n')
            finally:
                __M_buf, __M_writer = context._pop_buffer_and_writer()
                context.caller_stack._pop_frame()
            __M_writer(django_syntax(local)(__M_buf.getvalue()))
            return ''
        local = context.get('local', UNDEFINED)
        __M_writer = context.writer()
        __M_anon_1()
        __M_writer('\n\n')
        __M_anon_5()
        __M_writer('\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"48": 3, "50": 7, "19": 0, "39": 1, "56": 50, "28": 5}, "uri": "filters.html", "filename": "/Users/conan/Documents/data/programming/django-mako-plus/tests/templates/filters.html"}
__M_END_METADATA
"""
