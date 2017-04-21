# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1487769237.421188
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/teaching/2017/IS 411-413/fomoproject/homepage/templates/sections.html'
_template_uri = 'sections.html'
_source_encoding = 'utf-8'
import django_mako_plus
import os, os.path, re, json
_exports = ['header_maintenance', 'header_message222', 'header_menu_items_extra', 'body_section_before', 'body_section_left', 'body_section_right', 'content', 'body_section_after']


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
    return runtime._inherit_from(context, 'app_base.htm', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def header_menu_items_extra():
            return render_header_menu_items_extra(context._locals(__M_locals))
        def header_message222():
            return render_header_message222(context._locals(__M_locals))
        def header_maintenance():
            return render_header_maintenance(context._locals(__M_locals))
        def content():
            return render_content(context._locals(__M_locals))
        def body_section_before():
            return render_body_section_before(context._locals(__M_locals))
        request = context.get('request', UNDEFINED)
        def body_section_right():
            return render_body_section_right(context._locals(__M_locals))
        def body_section_after():
            return render_body_section_after(context._locals(__M_locals))
        def body_section_left():
            return render_body_section_left(context._locals(__M_locals))
        __M_writer = context.writer()
        __M_writer('\n\n\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'header_maintenance'):
            context['self'].header_maintenance(**pageargs)
        

        __M_writer('\n\n\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'header_message222'):
            context['self'].header_message222(**pageargs)
        

        __M_writer('\n\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'header_menu_items_extra'):
            context['self'].header_menu_items_extra(**pageargs)
        

        __M_writer('\n\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body_section_before'):
            context['self'].body_section_before(**pageargs)
        

        __M_writer('\n\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body_section_left'):
            context['self'].body_section_left(**pageargs)
        

        __M_writer('\n\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body_section_right'):
            context['self'].body_section_right(**pageargs)
        

        __M_writer('\n\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'content'):
            context['self'].content(**pageargs)
        

        __M_writer('\n\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body_section_after'):
            context['self'].body_section_after(**pageargs)
        

        __M_writer('\n\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header_maintenance(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def header_maintenance():
            return render_header_maintenance(context)
        __M_writer = context.writer()
        __M_writer('\n    Notice: We are performing maintenance tonight at 1am.\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header_message222(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def header_message222():
            return render_header_message222(context)
        __M_writer = context.writer()
        __M_writer('\n    <div class="alert alert-success alert-dismissible" role="alert">\n      <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>\n      Your password was changed successfully!\n    </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header_menu_items_extra(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def header_menu_items_extra():
            return render_header_menu_items_extra(context)
        request = context.get('request', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n    <li class="')
        __M_writer(str( 'active' if request.dmp_router_page == 'another' else '' ))
        __M_writer('"><a href="/">Another</a></li>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body_section_before(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body_section_before():
            return render_body_section_before(context)
        __M_writer = context.writer()
        __M_writer('\n    This is the "body section above" area that is between the header and column section.\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body_section_left(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body_section_left():
            return render_body_section_left(context)
        __M_writer = context.writer()
        __M_writer('\n    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body_section_right(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body_section_right():
            return render_body_section_right(context)
        __M_writer = context.writer()
        __M_writer('\n    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def content():
            return render_content(context)
        __M_writer = context.writer()
        __M_writer('\n    <h2>Sections with colors</h2>\n    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n    <h2>Sections with colors</h2>\n    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n    <h2>Sections with colors</h2>\n    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body_section_after(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body_section_after():
            return render_body_section_after(context)
        __M_writer = context.writer()
        __M_writer('\n    This is the "body section before" area that is between column section and the footer section.\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "/Users/conan/Documents/data/teaching/2017/IS 411-413/fomoproject/homepage/templates/sections.html", "uri": "sections.html", "source_encoding": "utf-8", "line_map": {"29": 0, "51": 1, "56": 7, "61": 16, "66": 21, "71": 26, "76": 31, "81": 36, "86": 46, "91": 51, "97": 5, "103": 5, "109": 11, "115": 11, "121": 19, "128": 19, "129": 20, "130": 20, "136": 24, "142": 24, "148": 29, "154": 29, "160": 34, "166": 34, "172": 39, "178": 39, "184": 49, "190": 49, "196": 190}}
__M_END_METADATA
"""
