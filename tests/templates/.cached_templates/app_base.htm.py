# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1491418883.488496
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/teaching/2017/IS 411-413/fomoproject/homepage/templates/app_base.htm'
_template_uri = 'app_base.htm'
_source_encoding = 'utf-8'
import django_mako_plus
import os, os.path, re, json
_exports = ['header_menu_items', 'header_menu_items_extra']


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
    return runtime._inherit_from(context, '/homepage/templates/base.htm', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        request = context.get('request', UNDEFINED)
        def header_menu_items():
            return render_header_menu_items(context._locals(__M_locals))
        def header_menu_items_extra():
            return render_header_menu_items_extra(context._locals(__M_locals))
        __M_writer = context.writer()
        __M_writer('\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'header_menu_items'):
            context['self'].header_menu_items(**pageargs)
        

        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header_menu_items(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        request = context.get('request', UNDEFINED)
        def header_menu_items():
            return render_header_menu_items(context)
        def header_menu_items_extra():
            return render_header_menu_items_extra(context)
        __M_writer = context.writer()
        __M_writer('\n    <li class="')
        __M_writer(str( 'active' if request.dmp_router_page == 'index' else '' ))
        __M_writer('"><a href="/">Home</a></li>\n    <li class="')
        __M_writer(str( 'active' if request.dmp_router_page == 'contact' else '' ))
        __M_writer('"><a href="/contact/">Contact</a></li>\n    <li class="')
        __M_writer(str( 'active' if request.dmp_router_page == 'about' else '' ))
        __M_writer('"><a href="/about/">About</a></li>\n    <li class="')
        __M_writer(str( 'active' if request.dmp_router_page == 'faq' else '' ))
        __M_writer('"><a href="/faq/">FAQ</a></li>\n    <li class="')
        __M_writer(str( 'active' if request.dmp_router_page == 'terms' else '' ))
        __M_writer('"><a href="/terms/">Terms</a></li>\n    <li class="')
        __M_writer(str( 'active' if request.dmp_router_page == 'sections' else '' ))
        __M_writer('"><a href="/sections/">Sections</a></li>\n    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'header_menu_items_extra'):
            context['self'].header_menu_items_extra(**pageargs)
        

        __M_writer('\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header_menu_items_extra(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def header_menu_items_extra():
            return render_header_menu_items_extra(context)
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "/Users/conan/Documents/data/teaching/2017/IS 411-413/fomoproject/homepage/templates/app_base.htm", "uri": "app_base.htm", "source_encoding": "utf-8", "line_map": {"29": 0, "39": 1, "49": 3, "58": 3, "59": 4, "60": 4, "61": 5, "62": 5, "63": 6, "64": 6, "65": 7, "66": 7, "67": 8, "68": 8, "69": 9, "70": 9, "75": 10, "81": 10, "92": 81}}
__M_END_METADATA
"""
