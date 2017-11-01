# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1509551115.109899
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/programming/django-mako-plus/tests/styles/static_files.cssm'
_template_uri = 'static_files.cssm'
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
        __M_writer('/* This is +providers.cssm+ */')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"24": 1, "19": 0, "30": 24}, "filename": "/Users/conan/Documents/data/programming/django-mako-plus/tests/styles/static_files.cssm", "uri": "static_files.cssm"}
__M_END_METADATA
"""
