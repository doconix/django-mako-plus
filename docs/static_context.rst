Sending Data to JS
================================

In the `tutorial <tutorial_css_js.html>`_, you learned to send context variables to ``*.js`` files using ``jscontext``:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function, jscontext
    from datetime import datetime

    @view_function
    def process_request(request):
        context = {
            jscontext('now'): datetime.now(),
        }
        return request.dmp.render('index.html', context)

Two providers in DMP go to work.  First, the ``JsContextProvider`` adds the values to its variable in context (initially created by ``dmp-common.js``). This script goes right into the generated html, which means the values can change per request.  Your script file uses these context variables, essentially allowing your Python view to influence Javascript files in the browser, even cached ones!

::

    <script>DMP_CONTEXT.set('u1234567890abcdef', { "now": "2020-02-11 09:32:35.41233"}, ...)</script>

Second, the ``JsLinkProvider`` adds a script tag for your script--immediately after the context.  The ``data-context`` attribute on this tag links it to your data in ``DMP_CONTEXT``.

::

    <script src="/static/homepage/scripts/index.js?1509480811" data-context="u1234567890abcdef"></script>

Serialization
------------------------------

The context dictionary is sent to Javascript using JSON, which places limits on the types of objects you can mark with ``jscontext``.  This normally means only strings, booleans, numbers, lists, and dictionaries are available.

However, there may be times when you need to send "full" objects.  When preparing the JS object, DMP looks for a class method named ``__jscontext__`` in the context values.  If the method exists on a value, DMP calls it and includes the return as the reduced, "JSON-compatible" version of the object.  The following is an example:

.. code:: python

    class NonJsonObject(object):
        def __init__(self):
            # this is a complex, C-based structure
            self.root = etree.fromString('...')

        def __jscontext__(self):
            # this return string is what DMP will place in the context
            return etree.tostring(self.root)


When you add a ``NonJsonObject`` instance to the render context, you'll still get the full ``NonJsonObject`` in your template code (since it's running on the server side). But it's reduced with ``instance.__jscontext__()`` to transit to the browser JS runtime:

.. code:: python

    def process_request(request):
        obj = NonJsonObject()
        context = {
            # DMP will call obj.__jscontext__() and send the result to JS
            jscontext('myobj'): obj,
        }
        return request.dmp.render('template.html', context)


Referencing the Context
-----------------------------

*Your script should immediately get a reference to the context data object*.  The Javascript global variable ``document.currentScript`` points at the correct ``<script>`` tag *on initial script run only*.  If you delay through ``async`` or a ready function, DMP will still most likely get the right context, but in certain cases (see below) you might get another script's context!

The following is a template for getting context data.  It retrieves the context immediately and creates a closure for scope:

::

    // arrow style
    (context => {
        // main code here
        console.log(context)
    })(DMP_CONTEXT.get())

    // function style
    (function(context) {
        // main code here
        console.log(context)
    })(DMP_CONTEXT.get())

Alternatively, the following is a template for getting context data **and** using a ``ready`` (onload) handler.  It retrieves the context reference immediately, but delays the main processing until document load is finished.

Delaying with jQuery ``ready()``:

::

    // arrow style
    $((context => () => {
        // main code here
        console.log(context)
    })(DMP_CONTEXT.get()))

    // function style
    $(function(context) {
        return function() {
            // main code here
            console.log(context)
        }
    }(DMP_CONTEXT.get()))

Delaying with pure Javascript:

::

    // arrow style
    document.addEventListener("DOMContentLoaded", (context => () => {
        // main code here
        console.log(context)
    })(DMP_CONTEXT.get()))

    // function style
    document.addEventListener("DOMContentLoaded", function(context) {
        return function() {
            // main code here
            console.log(context)
        }
    }(DMP_CONTEXT.get()))


Handling the "Certain Cases"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Above, we said that DMP could get the wrong context in "certain cases".  These are fringe issues, but you should handle them when developing libraries or widgets that might get ajax'd in many places.

Here's an example of when this might occur:

1. Your code uses jQuery.ajax() to retrieve ``snippet.html``, which has accompanying ``snippet.js`` and ``another.js`` files.
2. When jQuery receives the response, it strips the ``<script>`` element from the html.  The html is inserted in the DOM **without** the tag (this behavior is how jQuery is written -- it avoids a security issue by doing this).
3. jQuery executes the script code as a string, disconnected from the DOM.
4. Since DMP can't use the predictable ``document.currentScript`` variable, it defaults to the last-inserted context.  This is normally a good assumption.
5. However, suppose the two ``.js`` files were inserted during two different render() calls on the server. Two context dictionaries will be included in the html, and only one of them will be the "last" one.
6. Both scripts run with the same, incorrect context.  Do not pass Go. Do not collect $200. No context for you.

The solution is to help DMP by specifying the context by its ``app/template`` key:

::

    // look away Ma -- being explicit here!
    (function(context) {
        // your code here, such as
        console.log(context);
    })(DMP_CONTEXT.get('homepage/index'));

In the above code, DMP retrieves correct context by template name.  Even if the given template has been loaded twice, the latest one will be active (thus giving the right context).  Problem solved.

    A third alternative is to get the context by using a ``<script>`` DOM object as the argument to ``.get``. This approach always returns the correct context.

