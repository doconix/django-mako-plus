# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1544556954.7268622
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/programming/django-mako-plus/django_mako_plus/templates/stack_trace.html'
_template_uri = 'stack_trace.html'
_source_encoding = 'utf-8'
import django_mako_plus
import django.utils.html
import django_mako_plus
_exports = []


from mako.exceptions import syntax_highlight, pygments_html_formatter 

def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        bytes = context.get('bytes', UNDEFINED)
        len = context.get('len', UNDEFINED)
        self = context.get('self', UNDEFINED)
        isinstance = context.get('isinstance', UNDEFINED)
        tback = context.get('tback', UNDEFINED)
        min = context.get('min', UNDEFINED)
        range = context.get('range', UNDEFINED)
        max = context.get('max', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n')
        __M_writer('\n<style>\n    .stacktrace { margin:5px 5px 5px 5px; }\n    .highlight { padding:0px 10px 0px 10px; background-color:#9F9FDF; }\n    .nonhighlight { padding:0px; background-color:#DFDFDF; }\n    .sample { padding:10px; margin:10px 10px 10px 10px;\n                font-family:monospace; }\n    .sampleline { padding:0px 10px 0px 10px; }\n    .sourceline { margin:5px 5px 10px 5px; font-family:monospace;}\n    .location { font-size:80%; }\n    .highlight { white-space:pre; }\n    .sampleline { white-space:pre; }\n\n')
        if pygments_html_formatter:
            __M_writer('        ')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self, extra={'n_filter_on': True})(pygments_html_formatter.get_style_defs() ))
            __M_writer('\n        .linenos { min-width: 2.5em; text-align: right; }\n        pre { margin: 0; }\n        .syntax-highlighted { padding: 0 10px; }\n        .syntax-highlightedtable { border-spacing: 1px; }\n        .nonhighlight { border-top: 1px solid #DFDFDF;\n                        border-bottom: 1px solid #DFDFDF; }\n        .stacktrace .nonhighlight { margin: 5px 15px 10px; }\n        .sourceline { margin: 0 0; font-family:monospace; }\n        .code { background-color: #F8F8F8; width: 100%; }\n        .error .code { background-color: #FFBDBD; }\n        .error .syntax-highlighted { background-color: #FFBDBD; }\n')
        __M_writer('\n')
        __M_writer('    table.source {\n        background-color: #fdfdfd;\n    }\n    table.source > tbody > tr > th {\n        width: auto;\n    }\n    table.source > tbody > tr > td {\n        font-family: inherit;\n        white-space: normal;\n        padding: 15px;\n    }\n    #template {\n        background-color: #b3daff;\n    }\n\n</style>\n')


        src = tback.source
        line = tback.lineno
        if isinstance(src, bytes):
            src = src.decode()
        if src:
            lines = src.split('\n')
        else:
            lines = None
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['src','lines','line'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\n<h3>')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)(tback.errorname))
        __M_writer(': ')
        __M_writer(django_mako_plus.ExpressionPostProcessor(self)(tback.message))
        __M_writer('</h3>\n\n')
        if lines:
            __M_writer('    <div class="sample">\n    <div class="nonhighlight">\n')
            for index in range(max(0, line-4),min(len(lines), line+5)):
                __M_writer('        ')

                if pygments_html_formatter:
                    pygments_html_formatter.linenostart = index + 1
                
                
                __M_locals_builtin_stored = __M_locals_builtin()
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in [] if __M_key in __M_locals_builtin_stored]))
                __M_writer('\n')
                if index + 1 == line:
                    __M_writer('        ')

                    if pygments_html_formatter:
                        old_cssclass = pygments_html_formatter.cssclass
                        pygments_html_formatter.cssclass = 'error ' + old_cssclass
                    
                    
                    __M_locals_builtin_stored = __M_locals_builtin()
                    __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['old_cssclass'] if __M_key in __M_locals_builtin_stored]))
                    __M_writer('\n            ')
                    __M_writer(django_mako_plus.ExpressionPostProcessor(self, extra={'n_filter_on': True})(syntax_highlight(language='mako')(lines[index] )))
                    __M_writer('\n        ')

                    if pygments_html_formatter:
                        pygments_html_formatter.cssclass = old_cssclass
                    
                    
                    __M_locals_builtin_stored = __M_locals_builtin()
                    __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in [] if __M_key in __M_locals_builtin_stored]))
                    __M_writer('\n')
                else:
                    __M_writer('            ')
                    __M_writer(django_mako_plus.ExpressionPostProcessor(self, extra={'n_filter_on': True})(syntax_highlight(language='mako')(lines[index] )))
                    __M_writer('\n')
            __M_writer('    </div>\n    </div>\n')
        __M_writer('\n<div class="stacktrace">\n')
        for (filename, lineno, function, line) in tback.reverse_traceback:
            __M_writer('    <div class="location">')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self)(filename))
            __M_writer(', line ')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self)(lineno))
            __M_writer(':</div>\n    <div class="nonhighlight">\n    ')

            if pygments_html_formatter:
                pygments_html_formatter.linenostart = lineno
                
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in [] if __M_key in __M_locals_builtin_stored]))
            __M_writer('\n        <div class="sourceline">')
            __M_writer(django_mako_plus.ExpressionPostProcessor(self, extra={'n_filter_on': True})(syntax_highlight(filename)(line )))
            __M_writer('</div>\n    </div>\n')
        __M_writer('</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "/Users/conan/Documents/data/programming/django-mako-plus/django_mako_plus/templates/stack_trace.html", "uri": "stack_trace.html", "source_encoding": "utf-8", "line_map": {"19": 8, "21": 0, "34": 7, "35": 8, "36": 21, "37": 22, "38": 22, "39": 22, "40": 35, "41": 37, "42": 53, "56": 63, "57": 64, "58": 64, "59": 64, "60": 64, "61": 66, "62": 67, "63": 69, "64": 70, "65": 70, "72": 73, "73": 74, "74": 75, "75": 75, "83": 79, "84": 80, "85": 80, "86": 81, "93": 84, "94": 85, "95": 86, "96": 86, "97": 86, "98": 89, "99": 92, "100": 94, "101": 95, "102": 95, "103": 95, "104": 95, "105": 95, "106": 97, "113": 100, "114": 101, "115": 101, "116": 104, "122": 116}}
__M_END_METADATA
"""
