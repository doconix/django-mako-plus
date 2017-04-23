# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1492952745.431536
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/programming/django-mako-plus/tests/scripts/static_files.jsm'
_template_uri = 'static_files.jsm'
_source_encoding = 'utf-8'
import django_mako_plus
import os, os.path, re, json
from django_mako_plus import django_syntax, jinja2_syntax, alternate_syntax
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        __M_writer("console.log('This is +static_files.jsm+');\n")
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "/Users/conan/Documents/data/programming/django-mako-plus/tests/scripts/static_files.jsm", "source_encoding": "utf-8", "uri": "static_files.jsm", "line_map": {"24": 1, "19": 0, "30": 24}}
__M_END_METADATA
"""
