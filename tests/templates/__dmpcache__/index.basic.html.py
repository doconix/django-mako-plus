# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1519053308.105315
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/programming/django-mako-plus/tests/templates/index.basic.html'
_template_uri = 'index.basic.html'
_source_encoding = 'utf-8'
import django_mako_plus
import django_mako_plus
import os, os.path, re, json
from django_mako_plus import django_syntax, jinja2_syntax, alternate_syntax
_exports = ['content']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, 'base.htm', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def content():
            return render_content(context._locals(__M_locals))
        __M_writer = context.writer()
        __M_writer('\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'content'):
            context['self'].content(**pageargs)
        

        return ''
    finally:
        context.caller_stack._pop_frame()


def render_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def content():
            return render_content(context)
        __M_writer = context.writer()
        __M_writer('\n    <p>Hello world, this is DMP.</p>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "/Users/conan/Documents/data/programming/django-mako-plus/tests/templates/index.basic.html", "uri": "index.basic.html", "source_encoding": "utf-8", "line_map": {"48": 3, "60": 54, "54": 3, "38": 1, "31": 0}}
__M_END_METADATA
"""
