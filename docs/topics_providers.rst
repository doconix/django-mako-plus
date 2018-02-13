Static Files: Providers
================================

In the `tutorial <tutorial_css_js.html>`_, you learned how to automatically include CSS and JS based on your page name .
If your page is named ``mypage.html``, DMP will automatically include ``mypage.css`` and ``mypage.js`` in the page content.  Skip back to the `tutorial <tutorial_css_js.html>`_ if you need a refresher.

We'll now continue with the advanced version.

Javascript Matters
----------------------------------

Your ``base.htm`` file contains the following script link:

::

    <script src="/django_mako_plus/dmp-common.min.js"></script>

This file contains a few functions that DMP uses to run scripts and send context variables to your javascript.  It is important that this link be loaded **before** any DMP calls are done in your templates.

When running in production mode, your web server (IIS, Nginx, etc.) should serve this file rather than Django.  Or you may want to include the file in a bundler like webpack.  In any case, the file just needs to be included on every page of your site, so do it in an efficient way for your setup.

The following is an example setting for Nginx:

::

    location /django_mako_plus/dmp-common.min.js {
        alias /to/django_mako_plus/scripts/dmp-common.min.js;
    }

If you don't know the location of DMP on your server, try this command:

::

    python3 -c 'import django_mako_plus; print(django_mako_plus.__file__)'


(context) => { javascript }
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the `tutorial <tutorial_css_js.html>`_, you learned to send context variables to *.js files using ``jscontext``:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function, jscontext
    from datetime import datetime

    @view_function
    def process_request(request):
        context = {
            jscontext('now'): datetime.now(),
        }
        return request.render('index.html', context)

Two providers in DMP go to work.  First, the ``JsContextProvider`` adds the values to its variable in context (initially created by ``dmp-common.js``). This script goes right into the generated html, which means the values can change per request.  Your script file uses these context variables, essentially allowing your Python view to influence Javascript files in the browser, even cached ones!

::

    <script>DMP_CONTEXT.set('u1234567890abcdef', { "now": "2020-02-11 09:32:35.41233"}, ...)</script>

Second, the ``JsLinkProvider`` adds a script tag for your script--immediately after the context.  The ``data-context`` attribute on this tag links it to your data in ``DMP_CONTEXT``.

::

    <script src="/static/homepage/scripts/index.js?1509480811" data-context="u1234567890abcdef"></script>

|

    *Your script should immediately get a reference to the context data object*.  The Javascript global variable ``document.currentScript`` points at the correct ``<script>`` tag *on initial script run only*.  If you delay through ``async`` or a ready function, DMP will still most likely get the right context, but in certain cases (see below) you might get another script's context!

|

The following is a template for getting context data.  It retrieves the context immediately and creates a closure for scope:

::

    (function(context) {
        // main code here
        console.log(context);
    })(DMP_CONTEXT.get());

Alternatively, the following is a template for getting context data **and** using a ``ready`` (onload) handler.  It retrieves the context reference immediately, but delays the main processing until document load is finished.

Delaying with jQuery ``ready()``:

::

    $(function(context) {
        return function() {
            // main code here
            console.log(context);
        }
    }(DMP_CONTEXT.get()));

Delaying with pure Javascript:

::

    document.addEventListener("DOMContentLoaded", function(context) {
        return function() {
            // main code here
            console.log(context);
        }
    }(DMP_CONTEXT.get()));


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


Bundlers
---------------------

Getting fancy with something like Webpack, Browserify, or another bundler?  DMP scripts can go into your bundles, just like everything else.

Normally, DMP automatically includes ``<script>`` tags for your templates.  This behavior happens because ``{ 'provider': 'django_mako_plus.JsLinkProvider' }`` is in your settings file.  Remove this to stop the automatic script tag creation.

To create app-level bundles of all .js files in each app, follow these steps:

1. Remove ``django_mako_plus.JsLinkProvider`` from your settings file. If all providers are commented out, uncomment the other providers but continue to omit this one.  DMP will no longer add ``<script>`` tags for templates.
2. Ensure ``django_mako_plus.JsContextProvider`` is still active in settings. This will continue to add context variables to the ``DMP_CONTEXT`` javascript object.
3. Configure your bundler tool to bundle and minify ``*.js`` files in each app.  Create a link to these bundle files in your html templates (a per-app super template would be a great location).
4. Since the javascript files for all templates in a given app are bundled together, add ``if`` statements to each script to run only when their template is current. You could test the url in ``window.location``, a ``js_context()`` context variable, or template name in ``DMP_CONTEXT``.

Suppose your template is named, ``mytemplate.html``. The paired JS file, ``mytemplate.js``, might contain the following:

::

    (function(context) {
        // if context is not undefined, mytemplate was rendered
        if (context) {
            // behavior here!
        }
    })(DMP_CONTEXT.get('homepage/mytemplate'));


Preprocessors (Scss and Less)
-----------------------------------

If you are using preprocessors for your CSS or JS, DMP can automatically compile files.  While this could alternatively be done with an editor plugin or with a 'watcher' process, letting DMP compile for you keeps the responsibility within your project settings (rather than per-programmer-dependent setups).

Suppose your template ``index.html`` contains the typical code:

.. code:: html

    <head>
        ${ django_mako_plus.links(self) }
    </head>

When enabled, DMP looks for ``app_folder/styles/index.scss``.  If it exists, DMP checks the timestamp of the compiled version, ``app_folder/styles/index.css``, to see if if recompilation is needed.  If needed, it runs ``scss`` before generating ``<link type="text/css" />`` for the file.

During development, this check is done every time the template is rendered.  During production, this check is done only once -- the first time the template is rendered.

Rendering Other Pages
------------------------------

But suppose you need to autorender the JS or CSS from a page *other than the one currently rendering*?  For example, you need to include the CSS and JS for ``otherpage.html`` while ``mypage.html`` is rendering.  This is a bit of a special case, but it has been useful at times.

To include CSS and JS by name, use the following within any template on your site (``mypage.html`` in this example):

::

    ## instead of using the normal:
    ## ${ django_mako_plus.links(self) }
    ##
    ## specify the app and page name:
    ${ django_mako_plus.template_links(request, 'homepage', 'otherpage.html', context)


Rendering Nonexistent Pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This special case is for times when you need the CSS and JS autorendered, but don't need a template for HTML.  The ``force`` parameter allows you to force the rendering of CSS and JS files, even if DMP can't find the HTML file.   Since ``force`` defaults True, the calls just above will render even if the template isn't found.

In other words, this behavior already happens; just use the calls above.  Even if ``otherpage.html`` doesn't exist, you'll get ``otherpage.css`` and ``otherpage.js`` in the current page content.


Groups
-----------------

Each provider class specifies a "group" it is part of. In the default providers, the two groups are ``scripts`` and ``styles``.  When you render the static file links in your template, providers from all groups are included:

::

    ${ django_mako_plus.links(self) }

However, if you need to split the link rendering into two or more places on a page, or if you only need style links for some reason, you can specify a group in the render:

::

    ${ django_mako_plus.links(self, group='styles') }

In the above call, only providers in the ``styles`` group are printed.

Groups are specified in the options for each provider, so you can change them to any string you need in the ``CONTENT_PROVIDERS`` section.

Under the Hood: Providers
-------------------------------

The framework is built to be extended for custom file types.  When you call ``links()`` within a template, DMP iterates through a list of providers (``django_mako_plus.BaseProvider`` subclasses).  You can customize the behavior of these providers in your ``settings.py`` file.  Here's a very basic version:

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    # compiles app/styles/template.scss to app/styles/template/css
                    { 'provider': 'django_mako_plus.CompileScssProvider' },

                    # compiles app/styles/template.less to app/styles/template/css
                    { 'provider': 'django_mako_plus.CompileLessProvider' },

                    # generates links for app/styles/template.css
                    { 'provider': 'django_mako_plus.CssLinkProvider' },

                    # adds JS context
                    { 'provider': 'django_mako_plus.JsContextProvider' },

                    # generates links for app/scripts/template.js
                    { 'provider': 'django_mako_plus.JsLinkProvider' },
                ],
            }
        }
    ]

Each type of provider takes additional settings that allow you to customize locations, automatic compilation, etc.  When reading most options, DMP runs the option through str.format() with the following formatting kwargs:

* {appname} - The app name for the template being rendered.
* {template} - The name of the template being rendered, without its extension.
* {appdir} - The app directory for the template being rendered (full path).
* {staticdir} - The static directory as defined in settings.

    **Order Matters:**  Just like Django middleware, the providers are run in order.  If one provider depends on the work of another, be sure to list them in the right order.  For example, the ``JsContextProvider`` provides context variables for scripts, so it must be placed before ``JsLinkProvider``.  That way, the variables are loaded when the scripts run.

The following more-detailed version enumerates all the options (set to their defaults).

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    # compiles app/styles/template.scss to app/styles/template/css
                    {
                        'provider': 'django_mako_plus.CompileScssProvider'
                        'group': 'styles',
                        'source': '{appdir}/styles/{template}.scss',
                        'output': '{appdir}/styles/{template}.css',
                        'command': [ shutil.which('scss'), '--unix-newlines', '{appdir}/styles/{template}.scss', '{appdir}/styles/{template}.css' ],
                    },

                    # compiles app/styles/template.less to app/styles/template/css
                    {
                        'provider': 'django_mako_plus.CompileLessProvider'
                        'group': 'styles',
                        'source': '{appdir}/styles/{template}.less',
                        'output': '{appdir}/styles/{template}.css',
                        'command': [ shutil.which('lessc'), '--source-map', '{appdir}/styles/{template}.less', '{appdir}/styles/{template}.css' ],
                    },

                    # generates links for app/styles/template.css
                    {
                        'provider': 'django_mako_plus.CssLinkProvider'
                        'group': 'styles',
                        'filename': '{appdir}/styles/{template}.css',
                        'skip_duplicates': True,
                    },

                    # adds JS context
                    {
                        'provider': 'django_mako_plus.JsContextProvider'
                        'group': 'scripts',
                        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
                    },

                    # generates links for app/scripts/template.js
                    {
                        'provider': 'django_mako_plus.JsLinkProvider'
                        'group': 'scripts',
                        'filename': '{appdir}/scripts/{template}.js',
                        'async': False,
                    },
                ],
            }
        }
    ]

As an example, consider the `Transcrypt files <https://www.transcrypt.org/>`_ project, which transpiles Python code into Javascript. It lets you write browser scripts in our favorite language (note the source looks for ``.py`` files. The provider settings tells DMP to compile your Transcrypt files when needed. The first provider transpiles the source, and the second one creates the ``<script>`` link to the output file.

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    {
                        'provider': 'django_mako_plus.CompileProvider',
                        'group': 'scripts',
                        'source': '{appdir}/scripts/{template}.py',
                        'output': '{appdir}/scripts/__javascript__/{template}.js',
                        'command': [ 'transcrypt', '--map', '--build', '--nomin', '{appdir}/scripts/{template}.py' ],
                    },
                    {
                        'provider': 'django_mako_plus.JsLinkProvider',
                        'group': 'scripts',
                        'filename': '{appdir}/scripts/__javascript__/{template}.js',
                    },
                ],
            }
        }
    ]


Custom Providers
^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose you need custom preprocessing of static files or custom template content.  Your future may include creating a new provider class. Fortunately, these are pretty simple classes. Once you create the class, simply reference it in your settings.py file.

.. code:: python

    from django_mako_plus import BaseProvider
    from django_mako_plus.utils import merge_dicts

    class YourCustomProvider(BaseProvider):
        default_options = merge_dicts(BaseProvider.default_options, {
            'any': 'additional',
            'options': 'should',
            'be': 'specified',
            'here': '.',
        })

    def start(self, provider_run, data):
        '''
        Called on the *main* template's provider list as the run starts.
        Initialize values in the data dictionary here.
        '''
        pass

    def provide(self, provider_run, data):
        '''Called on *each* template's provider list in the chain - use provider_run.write() for content'''
        pass

    def finish(self, provider_run, data):
        '''
        Called on the *main* template's provider list as the run finishes
        Finalize values in the data dictionary here.
        '''
        pass

