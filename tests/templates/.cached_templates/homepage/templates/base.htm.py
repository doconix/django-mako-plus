# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1491418883.498962
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/teaching/2017/IS 411-413/fomoproject/homepage/templates/base.htm'
_template_uri = '/homepage/templates/base.htm'
_source_encoding = 'utf-8'
import django_mako_plus
import os, os.path, re, json
_exports = ['head_title', 'head_extra', 'header_maintenance', 'header_message', 'body_container', 'header_menu_items', 'body_section_before', 'body_section_top', 'body_section_left', 'body_section_right', 'content', 'body_section_after', 'body_footer']


from datetime import datetime 

def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def body_section_before():
            return render_body_section_before(context._locals(__M_locals))
        def head_title():
            return render_head_title(context._locals(__M_locals))
        def body_footer():
            return render_body_footer(context._locals(__M_locals))
        def header_menu_items():
            return render_header_menu_items(context._locals(__M_locals))
        self = context.get('self', UNDEFINED)
        def head_extra():
            return render_head_extra(context._locals(__M_locals))
        def body_section_after():
            return render_body_section_after(context._locals(__M_locals))
        user = context.get('user', UNDEFINED)
        def header_maintenance():
            return render_header_maintenance(context._locals(__M_locals))
        def body_section_right():
            return render_body_section_right(context._locals(__M_locals))
        def content():
            return render_content(context._locals(__M_locals))
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        def body_container():
            return render_body_container(context._locals(__M_locals))
        def body_section_left():
            return render_body_section_left(context._locals(__M_locals))
        def header_message():
            return render_header_message(context._locals(__M_locals))
        def body_section_top():
            return render_body_section_top(context._locals(__M_locals))
        request = context.get('request', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('<!DOCTYPE html>\n<html>\n    <meta charset="UTF-8">\n    <head>\n\n        <title>')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'head_title'):
            context['self'].head_title(**pageargs)
        

        __M_writer('</title>\n\n')
        __M_writer('        <script src="')
        __M_writer(str( STATIC_URL ))
        __M_writer('homepage/media/jquery.js"></script>\n        <script src="')
        __M_writer(str( STATIC_URL ))
        __M_writer('homepage/media/bootstrap/js/bootstrap.js"></script>\n        <script src="')
        __M_writer(str( STATIC_URL ))
        __M_writer('homepage/media/jquery.datetimepicker.full.js"></script>\n        <script src="')
        __M_writer(str( STATIC_URL ))
        __M_writer('homepage/media/jquery.form.js"></script>\n\n        <link rel="stylesheet" type="text/css" href="')
        __M_writer(str( STATIC_URL ))
        __M_writer('homepage/media/bootstrap/css/bootstrap.css" />\n        <link rel="icon" type="image/png" href="')
        __M_writer(str( STATIC_URL ))
        __M_writer('homepage/media/favicon.png"/>\n        <link rel="stylesheet" type="text/css" href="')
        __M_writer(str( STATIC_URL ))
        __M_writer('homepage/media/jquery.datetimepicker.min.css" />\n\n')
        __M_writer('        ')
        __M_writer(str( django_mako_plus.link_css(self) ))
        __M_writer('\n\n        ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'head_extra'):
            context['self'].head_extra(**pageargs)
        

        __M_writer('\n    </head>\n    <body>\n        <div id="header_maintenance">\n            ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'header_maintenance'):
            context['self'].header_maintenance(**pageargs)
        

        __M_writer('\n        </div>\n\n        <div id="header_message">\n            ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'header_message'):
            context['self'].header_message(**pageargs)
        

        __M_writer('\n        </div>\n\n        ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body_container'):
            context['self'].body_container(**pageargs)
        

        __M_writer('<!-- body_container -->\n\n')
        __M_writer('        ')
        __M_writer(str( django_mako_plus.link_js(self) ))
        __M_writer('\n\n    </body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_head_title(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def head_title():
            return render_head_title(context)
        __M_writer = context.writer()
        __M_writer('FOMO')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_head_extra(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def head_extra():
            return render_head_extra(context)
        __M_writer = context.writer()
        __M_writer('\n        ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header_maintenance(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def header_maintenance():
            return render_header_maintenance(context)
        __M_writer = context.writer()
        __M_writer('\n            ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header_message(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def header_message():
            return render_header_message(context)
        __M_writer = context.writer()
        __M_writer('\n')
        __M_writer('            ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body_container(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body_section_before():
            return render_body_section_before(context)
        def body_section_after():
            return render_body_section_after(context)
        user = context.get('user', UNDEFINED)
        def body_section_right():
            return render_body_section_right(context)
        def content():
            return render_content(context)
        def body_container():
            return render_body_container(context)
        def body_section_left():
            return render_body_section_left(context)
        def body_section_top():
            return render_body_section_top(context)
        def body_footer():
            return render_body_footer(context)
        def header_menu_items():
            return render_header_menu_items(context)
        request = context.get('request', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n\n            <header id="body_header">\n                <div id="header_icon">\n                    <a href="/" title="FOMO Home Page">\n                        <img src="/static/homepage/media/fomo.png" alt="FOMO Icon"/>\n                    </a>\n                </div>\n                <nav id="header_navbar" class="navbar navbar-default">\n                  <div class="container-fluid">\n                    <!-- Collect the nav links, forms, and other content for toggling -->\n                    <div class="collapse navbar-collapse">\n                      <ul class="nav navbar-nav navbar-right">\n                        ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'header_menu_items'):
            context['self'].header_menu_items(**pageargs)
        

        __M_writer('\n')
        if user.is_authenticated:
            __M_writer('                            <li class="dropdown">\n                              <a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Welcome, Conan <span class="caret"></span></a>\n                              <ul class="dropdown-menu">\n                                <li><a href="/account/index/"><span class="glyphicon glyphicon-user"></span> My Account</a></li>\n                                <li role="separator" class="divider"></li>\n                                <li><a href="/account/logout/"><span class="glyphicon glyphicon-log-out"></span> Logout</a></li>\n                              </ul>\n                            </li>\n')
        else:
            __M_writer('                            <li><a href="/account/login/">Login</a></li>\n')
        if request.user.is_authenticated():
            __M_writer('                            <li><button class="btn btn-success">Cart: <span id="cart_count_span" class="badge">')
            __M_writer(str( request.user.get_cart_count() ))
            __M_writer('</span></button></li>\n')
        __M_writer('                      </ul>\n                    </div><!-- /.navbar-collapse -->\n                  </div><!-- /.container-fluid -->\n                </nav>\n            </header>\n\n            <div id="body_section_before">\n                ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body_section_before'):
            context['self'].body_section_before(**pageargs)
        

        __M_writer('\n            </div>\n\n            <div id="body_section">\n                <div id="body_section_top">\n                    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body_section_top'):
            context['self'].body_section_top(**pageargs)
        

        __M_writer('\n                </div>\n\n                <div id="body_section_left">\n                    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body_section_left'):
            context['self'].body_section_left(**pageargs)
        

        __M_writer('\n                </div>\n\n')
        __M_writer('                <div id="body_section_right">\n                    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body_section_right'):
            context['self'].body_section_right(**pageargs)
        

        __M_writer('\n                </div>\n\n                <div id="body_section_content">\n                    ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'content'):
            context['self'].content(**pageargs)
        

        __M_writer('\n                </div>\n\n            </div><!-- body_section -->\n\n            <div id="body_section_after">\n                ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body_section_after'):
            context['self'].body_section_after(**pageargs)
        

        __M_writer('\n            </div>\n\n            <footer id="body_footer">\n                ')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'body_footer'):
            context['self'].body_footer(**pageargs)
        

        __M_writer('\n            </footer><!-- body_footer -->\n\n\n        ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header_menu_items(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def header_menu_items():
            return render_header_menu_items(context)
        __M_writer = context.writer()
        __M_writer('\n                        ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body_section_before(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body_section_before():
            return render_body_section_before(context)
        __M_writer = context.writer()
        __M_writer('\n                ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body_section_top(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body_section_top():
            return render_body_section_top(context)
        __M_writer = context.writer()
        __M_writer('\n                    ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body_section_left(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body_section_left():
            return render_body_section_left(context)
        __M_writer = context.writer()
        __M_writer('\n                    ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body_section_right(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body_section_right():
            return render_body_section_right(context)
        __M_writer = context.writer()
        __M_writer('\n                    ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def content():
            return render_content(context)
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body_section_after(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body_section_after():
            return render_body_section_after(context)
        __M_writer = context.writer()
        __M_writer('\n                ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body_footer(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def body_footer():
            return render_body_footer(context)
        __M_writer = context.writer()
        __M_writer('\n                    ')
        __M_writer('\n                    &copy; Copyright ')
        __M_writer(str( datetime.now().year ))
        __M_writer('.  All rights reserved.\n                ')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "/Users/conan/Documents/data/teaching/2017/IS 411-413/fomoproject/homepage/templates/base.htm", "uri": "/homepage/templates/base.htm", "source_encoding": "utf-8", "line_map": {"18": 110, "20": 0, "55": 1, "60": 6, "61": 9, "62": 9, "63": 9, "64": 10, "65": 10, "66": 11, "67": 11, "68": 12, "69": 12, "70": 14, "71": 14, "72": 15, "73": 15, "74": 16, "75": 16, "76": 19, "77": 19, "78": 19, "83": 22, "88": 27, "93": 36, "98": 116, "99": 119, "100": 119, "101": 119, "107": 6, "113": 6, "119": 21, "125": 21, "131": 26, "137": 26, "143": 31, "149": 31, "150": 36, "156": 39, "180": 39, "185": 53, "186": 54, "187": 55, "188": 63, "189": 64, "190": 66, "191": 67, "192": 67, "193": 67, "194": 69, "199": 77, "204": 83, "209": 88, "210": 92, "215": 94, "220": 98, "225": 105, "230": 112, "236": 52, "242": 52, "248": 76, "254": 76, "260": 82, "266": 82, "272": 87, "278": 87, "284": 93, "290": 93, "296": 98, "307": 104, "313": 104, "319": 109, "325": 109, "326": 110, "327": 111, "328": 111, "334": 328}}
__M_END_METADATA
"""
