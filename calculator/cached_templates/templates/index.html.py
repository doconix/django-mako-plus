# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1382157646.529026
_enable_loop = True
_template_filename = '/Users/conan/Documents/data/programming/django-mako/calculator/templates/index.html'
_template_uri = 'index.html'
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
        def content():
            return render_content(context._locals(__M_locals))
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer('\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'content'):
            context['self'].content(**pageargs)
        

        # SOURCE LINE 55
        __M_writer('  \n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def content():
            return render_content(context)
        __M_writer = context.writer()
        # SOURCE LINE 4
        __M_writer('\n  <p>\n    Welcome to our home page!  This page explores the primary benefits of the mako_controller in Django.\n  </p>\n  <h2>URL Matching by Convention - Sound Pythonic?</h2>\n  <p>\n    This file is just a simple HTML file.  There\'s no view function associated with it.  The controller\n    first looks for <tt>/calculator/views/index.py</tt> -> <tt>process_request()</tt>, and when it doesn\'t find the function, it\n    renders the <tt>/calculator/templates/index.html</tt> file directly.\n  </p>    \n  <p>\n    In other words, this index page is a great example of the mako_controller.  Instead of putting an entry in urls.py\n    for every. single. page. on. your. site (the normal Django way), it uses a convention to know which pages can be\n    displayed.  \n  </p>\n  <h2>Automatic CSS and Javascript Inclusion</h2>\n  <p>\n    In addition, the parent template of this file (<tt>base/templates/base.htm</tt>) automatically includes styles and scripts\n    for each template in the inheritance chain.  For example, this index page has the following inheritance:\n    <ol>\n      <li>Base template: <tt>/base/templates/base.htm</tt></li>\n      <li>Child template: <tt>/calculator/templates/index.html</tt></li>\n    </ol>\n    Because of this chain, the following styles and scripts are automatically included in the rendered page:\n    <ol>\n      <li><tt>/base/styles/base.css</tt></li>\n      <li><tt>/base/styles/base.cssm</tt> (this one can contain dynamic Python code)</li>\n      <li><tt>/calculator/styles/index.css</tt></li>\n      <li><tt>/calculator/styles/index.cssm</tt> (this one can contain dynamic Python code)</li>\n      <li><tt>/base/scripts/base.js</tt></li>\n      <li><tt>/base/scripts/base.jsm</tt> (this one can contain dynamic Python code)</li>\n      <li><tt>/calculator/scripts/index.js</tt></li>\n      <li><tt>/calculator/scripts/index.jsm</tt> (yep, you guessed it, this one can contain dynamic Python code)</li>\n    </ol>\n    Of course, you\'d rarely create all the above files.  Just create the ones that you need.  For example, if you have \n    CSS that affects the dom elements in <tt>base.htm</tt>, place it in <tt>base.css</tt> or <tt>base.cssm</tt>.  If you have Javascript that affects \n    the dom elements in <tt>index.html</tt>, place it in <tt>index.js</tt> or <tt>index.jsm</tt>.\n  </p>\n  <p>\n    The above "automatic" inclusion of .css and .js files creates a nice separation of HTML, CSS, and JS code, and it \n    provies a place to attach styles and scripts at the same inheritance level as the HTML they affect.  It also \n    speeds up browser rendering because all the CSS and JS are included right in the HTML file - circumventing\n    further requests on your system (even though you\'re really keeping things separate on the coding side).\n  </p>\n  <h2>A More Complete Example</h2>\n  <p>\n    Try out the calculator app for a more complex example.\n  </p>\n  <ul>\n    <li><a href="/calculator/calc/">A calculator app</a></li>\n  </ul>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


