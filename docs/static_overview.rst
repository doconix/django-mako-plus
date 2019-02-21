.. _static_overview:

Overview
================================

    This page details how DMP supports traditional links. If you've moved on to bundling instead of direct links, these are not the droids you're looking for. Move along to the `bundling page </static_webpack.html>`_.

In the `tutorial <tutorial_css_js.html>`_, you learned how to automatically include CSS and JS based on your page name .
If your page is named ``mypage.html``, DMP will automatically include ``mypage.css`` and ``mypage.js`` in the page content.  Skip back to the `tutorial <tutorial_css_js.html>`_ if you need a refresher.

Here's what DMP can do for your static files:

:Automatic Links:
    Suppose ``index.html`` inherits from two supertemplates, and you have a ``.js`` file and a ``.css`` file for each:

    .. code-block:: sh

        base.htm        (base.js, base.css)
            |
        homepage.htm    (homepage.js, homepage.css)
            |
        index.html      (index.js, index.css)

    Why so many files for a single web page? It's a scoping issue. Since ``base.htm`` is the ancestor of **every** page on our site, its related JS and CSS link into every page. If a CSS style affects every page (such as the top menubar), it goes in ``base.css``. In like manner, the static files for ``homepage`` link into the pages of the homepage app. Put the code in the level for its scope.

    When ``index.html`` renders, DMP automatically creates the links for its support pages. That's all six files in this case!

:Inject Variables into Javascript:
    Custom variables are easy to send from view's ``process_request`` function to the rendering template scope (just put it in ``context`` when calling render). But getting values from ``process_request`` to the browser's Javascript scope is a bit more difficult. It requires encoding to JSON and html-based script tags. DMP makes it easy (just wrap the key with ``jscontext(...)`` when placing in the render context.

:Sass and Less Compiling:
    Just before DMP links the related CSS files into a page, it can run ``sass`` or ``lessc`` for you. I realize other options exist for this (editors, watchers), but personally, I prefer it because compilation happens via my project settings. If this benefits your workflow, it's here waiting...

:Webpack Bundling:
    Bundling vendor support files is pretty easy, but things get a little more difficult when page-specific code gets bundled. DMP allows appwide bundles, and it automatically runs the right bundle code for each page.



How It Works
-------------------

Open ``base.htm`` and look at the following code:

::

    ## render the static file links for this template
    ${ django_mako_plus.links(self) }

The call to ``links(self)`` triggers a number of "provider" classes to run. Each provider is responsible for adding specific types of links. For example, the ``JsContextProvider`` adds context variables to the rendered page; the ``CssLinkProvider`` adds ``<link rel="stylesheet"...>`` links for CSS files related to the current page (and its ancestors).

Since this call to ``links(self)`` exists in ``base.htm`` (and since all site pages extend from base), these providers trigger on every page of your site. Just be sure your pages extend from this supertemplate.

    DMP's default app (homepage) contains two "base" files: ``base.htm`` and ``base_ajax.htm``.  The first is for full pages (you know, the ones that start with ``<html>`` :).  The second is for page snippets like those created in ajax requests. Pretty much the only thing in ``base_ajax.htm`` is the call to links and a block for subpages to override.

``dmp-common.js``
----------------------------------

Lets go back to ``base.htm``.  Just above the call to ``links(self)`` you'll see the following:

::

    <script src="/django_mako_plus/dmp-common.min.js"></script>

DMP uses this script to make everything work on the browser side. For example, this script injects values sent from your view.py into the client-side JS scope. It's a small script (3K), and it's written in old-school Javascript (for a wide browser audience).

When running in production mode, your web server (IIS, Nginx, etc.) should serve this file (rather than Django).  Or it could be bundled with other vendor code. In any case, the file just needs to be included on every page of your site.

The following is an example setting for Nginx:

::

    location /django_mako_plus/dmp-common.min.js {
        alias /to/django_mako_plus/scripts/dmp-common.min.js;
    }

If you don't know the location of DMP on your server, try this command:

::

    python3 -c 'import django_mako_plus; print(django_mako_plus.__file__)'


Passing Data: View :raw-html:`&rarr;` JSON :raw-html:`&rarr;` JS
---------------------------------------------------------------------

Getting data from server-side, Python view files (e.g. ``process_request`` functions) to the client-side, browser JS scope can be difficult. The `tutorial introduced this issue <tutorial_css_js.html>`_ with a simple example: accessing the server's current time in your JS code.

Normally, ``.js`` files are static, meaning they don't change from one request to another. (We actually **could** render JS and CSS files the same way we render templates, but writing meta code that writes JS is reserved for special, unmentionable cases.)

Since we can't (aren't willing) to change the JS itself, a workaround is writing small script sections inside templates. While this method is common, it has some drawbacks. First, it mixes JS into HTML code. Second, it creates variables in the global window scope (so JS files can get to them).

Step 1: Mark Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We already have a mechanism to get values from ``process_request`` to templates: **the context dictionary**.  DMP just needs to know which keys/values you want pushed on to the browser scope. This is done by "marking" context keys with ``jscontext``:

.. code-block:: python

    from django.conf import settings
    from django_mako_plus import view_function, jscontext
    from datetime import datetime

    @view_function
    def process_request(request):
        context = {
            jscontext('now'): datetime.now(),
        }
        return request.dmp.render('index.html', context)

When your template calls DMP's ``links(self)`` method (see ``base.htm``), the first provider that goes to work is ``JsContextProvider``. This provider inspects the context dictionary for keys marked with ``jscontext``. It converts these values to JSON and inserts the first line below into your template. The next provider to run is ``JsLinkProvider``, which creates the second line below:

.. code-block:: html

    <script>DMP_CONTEXT.set(..., "ketkk4MY3rAXNipepsUrV", { "now": "2020-02-11 09:32:35.41233"}, ...)</script>
    <script src="/static/homepage/scripts/index.js" data-context="ketkk4MY3rAXNipepsUrV"></script>


Step 2: Use in Javascript
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In your JS files, you can access your variables in a context dictionary provided by a closure. In layman's terms, this means you should wrap the entire ``index.js`` file in an anonymous function with a parameter for the context dictionary. The following are three examples in ES5 and ES6:

+--------------------------------------------+-----------------------------------------------------------------------+-----------------------------------------------------------------------+
|                                            |  ES5 Javascript (function style)                                      |  ES6 Javascript (fat-arrow style)                                     |
+============================================+=======================================================================+=======================================================================+
| Run immediately                            | .. code-block:: text                                                  | .. code-block:: text                                                  |
|                                            |                                                                       |                                                                       |
|                                            |     (function(context) {                                              |     (context => {                                                     |
|                                            |         # your JS code here                                           |         # your JS code here                                           |
|                                            |         console.log(context['now']);                                  |         console.log(context['now'])                                   |
|                                            |     })(DMP_CONTEXT.get());                                            |     })(DMP_CONTEXT.get())                                             |
|                                            |                                                                       |                                                                       |
+--------------------------------------------+-----------------------------------------------------------------------+-----------------------------------------------------------------------+
| Run when page is ready (JQuery)            | .. code-block:: text                                                  | .. code-block:: text                                                  |
|                                            |                                                                       |                                                                       |
|                                            |     $(function(context) {                                             |     $((context => () => {                                             |
|                                            |         return function() {                                           |         # your JS code here                                           |
|                                            |             # your JS code here                                       |         console.log(context['now'])                                   |
|                                            |             console.log(context['now']);                              |     })(DMP_CONTEXT.get()))                                            |
|                                            |         }                                                             |                                                                       |
|                                            |     })(DMP_CONTEXT.get());                                            |                                                                       |
|                                            |                                                                       |                                                                       |
+--------------------------------------------+-----------------------------------------------------------------------+-----------------------------------------------------------------------+
| Run when page is ready (vanilla JS)        | .. code-block:: text                                                  | .. code-block:: text                                                  |
|                                            |                                                                       |                                                                       |
|                                            |     document.addEventListener("DOMContentLoaded", function(context) { |     document.addEventListener("DOMContentLoaded", (context => () => { |
|                                            |         return function() {                                           |         # your JS code here                                           |
|                                            |             # your JS code here                                       |         console.log(context['now'])                                   |
|                                            |             console.log(context['now']);                              |     })(DMP_CONTEXT.get()))                                            |
|                                            |         }                                                             |                                                                       |
|                                            |     }(DMP_CONTEXT.get()));                                            |                                                                       |
|                                            |                                                                       |                                                                       |
+--------------------------------------------+-----------------------------------------------------------------------+-----------------------------------------------------------------------+



Undefined Context?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If things aren't working, open your browser console/inspector and see if JS is giving you any messages.  The following are a few reasons that the context might be undefined:

* Your JS code is running too late.  If you reverse the closure functions, the code doesn't run in time to catch the context.  Compare your code with the examples below.
* You might be missing script lines ``<script src="/django_mako_plus/dmp-common.min.js"></script>`` and ``${ django_mako_plus.links(self) }``, or these might be reversed.
* ``/django_mako_plus/dmp-common.min.js`` might not be available.  Check for a 404 error in the Network tab of your browser's inspector.
* In rare situations (JQuery, I'm looking at you!), JS returned via ajax may not be able to find the right context. See the FAQ for more info.


Limitations
------------------------

The context dictionary is sent to Javascript using JSON, which places limits on the types of objects you can mark with ``jscontext``.  This normally means only strings, booleans, numbers, lists, and dictionaries work out of the box.


Custom JSON Encoding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There may be times when you need to send "full" objects.  When preparing the JS object, DMP looks for a class method named ``__jscontext__`` in the context values.  If the method exists on a value, DMP calls it and includes the return as the reduced, "JSON-compatible" version of the object.  The following is an example:

.. code-block:: python

    class MyNonJsonObject(object):
        def __init__(self):
            # this is a complex, C-based structure
            self.root = etree.fromstring('...')

        def __jscontext__(self):
            # this string is what DMP will place in the context
            return etree.tostring(self.root, encoding=str)


When you add a ``MyNonJsonObject`` instance to the render context, you'll still get the full ``MyNonJsonObject`` in your template code (since it's running on the server side). But it's reduced with ``instance.__jscontext__()`` to transit to the browser JS runtime:

.. code-block:: python

    def process_request(request):
        mnjo = MyNonJsonObject()
        context = {
            # DMP will call obj.__jscontext__() and send the result to JS
            jscontext('mnjo'): mnjo,
        }
        return request.dmp.render('template.html', context)

Now adjust your JS to parse the XML string, and you're back in business.
