# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1382157726.109034
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/programming/django-mako/calculator/templates/calc.html'
_template_uri = 'calc.html'
_source_encoding = 'ascii'
import os, os.path, re
from calculator import models as cmod
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
    return runtime._inherit_from(context, '/base/templates/base.htm', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        len = context.get('len', UNDEFINED)
        request = context.get('request', UNDEFINED)
        def content():
            return render_content(context._locals(__M_locals))
        form = context.get('form', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        calc = context.get('calc', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer('\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'content'):
            context['self'].content(**pageargs)
        

        # SOURCE LINE 67
        __M_writer('  \n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        len = context.get('len', UNDEFINED)
        request = context.get('request', UNDEFINED)
        def content():
            return render_content(context)
        form = context.get('form', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        calc = context.get('calc', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 4
        __M_writer("\n\n  <!-- URL parameters -->\n  <h2>URL Parameters:</h2>\n  <p>\n    Before we do the calculator app, check out the url parameters.  This function provides an alternative way to send data to your view functions.  \n    Instead of using forms or links with \n    embedded forms, such as /calculator/page?first=A&amp;second=B, you can instead send /calculator/page/A/B/.\n    The Mako controller will add the A and B values to the <tt>request.urlparams</tt> list.  The drawback is you\n    access the parameters by index rather than name.  The benefit is a much prettier URL, plus you have a second way \n    to send parameters.  In fact, these get really powerful when you need to send values <i>in addition</i> to form values.\n    Instead of having a number of hidden parameters in your form, you can add IDs to the url and use the form POST dict for\n    regular data.\n  </p>\n  <p>\n    These are an optional feature of the Mako controller, but I've found them incredibly useful in creating better &lt;a href&gt; \n    links and to send values around the pages of the site that don't need full forms.\n  </p>\n  \n")
        # SOURCE LINE 23
        if len(request.urlparams) > 0:
            # SOURCE LINE 24
            __M_writer('    <p>The url parameters sent in were:</p>\n')
            # SOURCE LINE 25
            for i, param in enumerate(request.urlparams):
                # SOURCE LINE 26
                __M_writer('      <div>')
                __M_writer(str( i ))
                __M_writer(': ')
                __M_writer(str( param ))
                __M_writer('</div>\n')
            # SOURCE LINE 28
        else:
            # SOURCE LINE 29
            __M_writer('    <p>There were no url parameters.  Try submitting the form and then looking at the url above.</p>\n')
        # SOURCE LINE 31
        __M_writer('\n  <!-- Example use of static url for graphics, css files, scripts, etc. -->\n  <img style="float: right;" src="')
        # SOURCE LINE 33
        __M_writer(str( STATIC_URL ))
        __M_writer('calculator/calc.gif"/>\n  <!-- Calculator -->\n  <h2>Calculator Example:</h2>\n')
        # SOURCE LINE 36
        if calc:
            # SOURCE LINE 37
            __M_writer('    <p>The last calculation was: ')
            __M_writer(str( calc ))
            __M_writer('</p>\n')
        # SOURCE LINE 39
        __M_writer('  \n  <p>New calcuation:</p>\n  <form action="/calculator/calc/A/B/C/" method="post">\n  ')
        # SOURCE LINE 42
        __M_writer(str( form.as_p() ))
        __M_writer('\n  <input type="submit" value="Submit"/>\n  </form>\n  \n  \n  <!-- Ajax buttons -->\n  <h2>Ajax Example:</h2>\n  <p id="calculator-log">Log not loaded yet.</p>\n  <button id="load-calculator-log">(Re)Load Log</button>\n  <button id="delete-calculator-log">Delete Log</button>\n  <script>\n    $(function() {\n      // load log click\n      $(\'#load-calculator-log\').click(function() {\n        $(\'#calculator-log\').load(\'/calculator/calc__loadlog/\');\n      });//click\n\n      // delete log click\n      $(\'#delete-calculator-log\').click(function() {\n        $(\'#calculator-log\').load(\'/calculator/calc__deletelog/\');\n      });//click\n    });//func\n  </script>\n\n  \n')
        return ''
    finally:
        context.caller_stack._pop_frame()


