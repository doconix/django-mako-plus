.. _static_faq:

FAQ
====================================

Why aren't DMP log messages showing in my browser console?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DMP's debug messages make bundling more transparent. They can be lifesavers at times, but they can be bothersome once things are working. For more background, read the previous question on how to turn off log messages.

The following must happen for debug messages to show in the browser console:

* The ``django_mako_plus`` logger must be set to DEBUG.
* Very few messages show in the normal providers, so you won't see many there. Since webpack provider is where transparency is needed, it's where messages are printed.
* On Chromium browsers, ``console.debug`` messages only print when "Verbose" is selected in the console.
* If you still can't get messages to print, try adding a few ``console.log`` lines to ``dmp-common.js``, especially in its log method. Hopefully that sorts things out.


Why is DMP blowing up my browser console?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tracing static file issues can be difficult, so DMP is written to make it as transparent as possible.  In particular, bundling is fraught with danger: functions might not link right, contexts may trigger before bundles fully load, and in extreme cases, the Killer Rabbit of Caerbannog can show up. The debug messages in your browser console help you see exactly what's going on.

To turn these messages off, adjust the DMP logger in your settings to any level above DEBUG:

.. code-block:: python

    LOGGING = {
        ...
        'loggers': {
            ...
            'django_mako_plus': {
                'handlers': ['console_handler'],
                'level': 'WARNING',     # DMP messages in browser console only show if DEBUG
            },
        },
    }


Can DMP provide links for other templates?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose you need to autorender the JS or CSS from a page *other than the one currently rendering*?  For example, you need to include the CSS and JS for ``otherpage.html`` while ``mypage.html`` is rendering.  This is a bit of a special case, but it has been useful at times.

To include CSS and JS by name, use the following within any template on your site (``mypage.html`` in this example):

.. code-block:: html+mako

    ## instead of using the normal:
    ## ${ django_mako_plus.links(self) }
    ##
    ## specify the app and page name:
    ${ django_mako_plus.template_links(request, 'homepage', 'otherpage.html', context)


What if I need links but don't need a template?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This special case is for times when you need the CSS and JS autorendered, but don't need a template for HTML.  Use the same code as above, but add ``force=True``. DMP will render the CSS and JS files for the given template name, whether or not the template actually exists.

.. code-block:: html+mako

    ## renders links for `homepage/styles/otherpage.css` and `homepage/styles/otherpage.js`
    ${ django_mako_plus.template_links(request, 'homepage', 'otherpage.html', context, force=True)

However, I should note that having links without a template will probably confuse readers of your code because it breaks the convention. Unless you really do have a special case, I'd recommend creating an (empty) template anyway.


DMP is linking the wrong context. What's up?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When libraries play games with the loading process (JQuery, I'm looking at you!), the context can be difficult to find in some situations:

Here's an example of when this might occur:

1. Your code uses jQuery.ajax() to retrieve ``snippet.html``, which has accompanying ``snippet.js`` and ``another.js``.
2. When jQuery receives the response, it strips the ``<script>`` element from the html.  The html is inserted in the DOM **without** the tag (this behavior is how jQuery is written -- it avoids a security issue by doing this hack).
3. jQuery executes the script code as a string, disconnected from the DOM.
4. Since DMP can't use the predictable ``document.currentScript`` variable, it defaults to the last-inserted context.  This is normally a good assumption.
5. However, since two ``.js`` files were inserted, TWO context dictionaries are linked in DMP_CONTEXT. Only one of them will be the "last" one.
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



Bundling: How do I clear the generated bundle files?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a terminal (Mac, Linux, or Windows+GitBash), issue these commands:

::

    # careful, this is recursive!
    rm **/__entry__.js
    rm **/__bundle__.js


Bundling: How do I recreate ``__entry__.js`` files?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Webpack depends on the accuracy of your ``__entry__.js`` file, and it's important to keep it in sync with the files in your projects. There are two ways to recreate your entry files:

1. **Manual:** Run ``python3 manage.py dmp_webpack --overwrite`` to recreate the entry files in all apps.
2. **Automatic:** Whenever you render a page, DMP automatically reruns the ``dmp_webpack`` command to check for needed updates.

You can turn off automatic creation in the webpack provider options:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            ...
            'OPTIONS': {
                ...
                'CONTENT_PROVIDERS': [
                    { 'provider': 'django_mako_plus.JsContextProvider' },
                    {
                        'provider': 'django_mako_plus.WebpackJsLinkProvider',
                        'create_entry': False,
                    }
                ],
            },
        },
    ]


Bundling: Why does Webpack report errors whenever I add or delete files?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During development, webpack is normally running in "watch" mode. When your entry file gets out of sync with your actual project files, webpack gets grumpy. Refreshing the page a couple times usually brings everything back into sync.

For an example of why this is needed, consider this scenario:

1. You have three related files in your homepage app: ``homepage/templates/index.html``, ``homepage/styles/index.css``, and ``homepage/scripts/index.js``. You run the webpack management command, which creates ``homepage/scripts/__entry__.js`` with references to the two CSS and JS files.
2. You run the webpack watcher daemon, and it creates ``homepage/scripts/__bundle__.js``. Everything is in sync, and life is happy.
3. You develop for a bit, and each time you change the support files, webpack recreates the bundle. You pat webpack on the head and give it a treat.
4. You no longer need ``homepage/styles/index.css``, so you delete the file. This is where things go wrong for a bit... Webpack sees the changes, and it complains that a required file in ``homepage/scripts/__entry__.js`` no longer exists. A red error yells at you in the webpack console. The solution is to recreate your entry file, but DMP hasn't had a chance to do it. That chance comes when the index page gets rendered again.
5. You reload the index page in your browser. During template rendering (specifically, the ``WebpackJsLinkProvider`` provider), DMP recreates any entry files that are out of sync. Webpack sees changed entry file, and rebuilds your bundle.

    On Step 5, your browser might load the bundle before the webpack watcher recreates it. When this happens, refresh the page one more time to pull the new bundle.


Bundling: My functions are loading, but they don't trigger. Whaaaaat?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The DMP client-side script, ``dmp-common.min.js``, loads bundles using this process:

1.  set() is run, which creates a container for the context, template names, and inheritance.

2.  The browser reaches the bundle <script> tag and downloads the bundle file.

    a.  Once downloaded, the script runs and loads its template functions into the context container. We recheck if ready.

3.  checkContextReady() runs due to the script tag's onLoad= event. The script checks:

    a.  Are all template functions loaded?

            Suppose account/templates/login.html extends from homepage/templates/base.htm. Assuming app-based bundles, we're dealing with two bundles: the login bundle (login.js and login.css), and the homepage bundle contains base.js and base.css.  When the account bundle loads, we still don't have base.js or base.css, so we need to wait. When the homepage bundle loads, all four functions (login.js, login.css, base.js, and base.css) are loaded, so they can be called. Each time a template function loads, we recheck if ready.

    b.  Are all template functions imports resolved?

            The body of each template function contains dynamic import statements. So we can't just load the function itself, we need to run the function to and wait for the imports to resolve. It's done this way because we don't want ALL the imports on a given page -- the bundle contains the imports for all the pages in the app, not just for the current page. Each time a template function resolves, we recheck if ready.

    c.  Is context.pendingCalls > 0?  This variable allows delayed execution of the functions (read on).

4.  DMP_CONTEXT.callBundleContext() is called by a <script> tag in the template. This function increments context.pendingCalls and then rechecks if ready.

The constant rechecking allows #2, #3, and #4 to happen in any order--which supports async loading of scripts. If #4 occurs before #3, ``pendingCalls`` increments, but it doesn't trigger because its still waiting on bundle functions. When the bundles finally load and resolve, the check happens again and the bundle functions finally run.

With this understanding, here's some ideas for debugging:

1. Assuming the DMP logger is at ``DEBUG`` level, the process above is reported in detail in the browser console. Follow these log messages to see where the process breaks down. Check that all needed bundle functions get loaded and resolved, and check the value of ``pendingCalls``.

2. Disable DMP's automatic ``__entry__.js`` creation (``create_entry`` in the provider options). You can then insert console.log messages in ``__entry__.js`` to test things within the bundle.

3. Litter ``dmp-common.js`` (the unminified version) with console.log statements.


Bundling: How do I use Sass (Less, TypeScript, etc.) with DMP Webpack?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One benefit to bundling is the output files from compiles like ``sass`` are piped right into bundles instead of as extra files in your project. Here's the steps:

1. Clear out existing entry and bundle files (see above).
2. Install the Sass dependencies

::

    npm install --save-dev node-sass sass-loader

3. Modify ``webpack.config.js`` to find Sass files:

.. code-block:: js

    module.exports = {
        ...
        module: {
            rules: [
                ...
                {
                    test: /\.scss$/,
                    use: [
                        { loader: 'style-loader' },
                        { loader: 'css-loader' },
                        { loader: 'sass-loader' },
                    ]
                }
            ]
        },
    };

4. Configure ``settings.py`` to include ``app/styles/*.scss`` files wherever they match template names.

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            ...
            'OPTIONS': {
                ...
                'WEBPACK_PROVIDERS': [
                    { 'provider': 'django_mako_plus.CssLinkProvider' },
                    {
                        'provider': 'django_mako_plus.CssLinkProvider',
                        'filepath': lambda p: os.path.join(p.app_config.name, 'styles', p.template_relpath + '.scss'),
                    },
                    { 'provider': 'django_mako_plus.JsLinkProvider' },
                ],
            },
        },
    ]

Note in the above options, we're including ``.scss`` and ``.css`` (whenever they exist), so be sure to erase any generated ``.css`` files from previous runs of Sass. We only need the source ``.scss`` files in the ``styles`` subdir.

3. Recreate the entry files and compile the bundles:

::

    python3 manage.py dmp_webpack --overwrite
    npm run watch


Bundling: Can I bundle dmp-webpack.js?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Short answer:

::

    npm install django-mako-plus

Long answer: there's a few gotchas you need to watch for:

1.  Even when dmp-common is bundled, ``DMP_CONTEXT`` still needs to be available in the window object. It can't live entirely within the bundle scope because ``<script>`` context tags in the template need it. Hoisting to the window scope happens automatically, so just bundle away. This point is just an FYI when you see the variable still attached to the global scope. Hopefully we'll get around this at some point so it does live entirely within the bundle, but there are still some issues to work out.

2.  The bundle containing ``DMP_CONTEXT`` must load **before** the ``<script>`` context tags run.  If you view the source of the rendered HTML page, you can see where the bundle should load in relation to the ``<script>`` tags DMP injects into the page. Make sure the order is right.

3.  You can choose between two possible files to import:

    a.  The transpiled, browser-compatible, ES5 file. It has no external dependencies and should work anywhere. It's the default export on npm:

        ::

            import 'django-mako-plus';

    b.  The original ES6 source, before any webpack/babel modification. If you'd like to include the original file, this one's for you:

        ::

            import 'django-mako-plus/django_mako_plus/webroot/dmp-common.src.js';


Bundling: How do I create a vendor bundle?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the `tutorial </static_webpack.html>`_, we created one bundle per app.  These bundles can grow large as you enjoy the convenience of ``npm init`` and link to more and more things in ``node_modules/``. Since each bundle is self-contained, there will be a lot of duplication between bundles. For example, the webpack bootstrapping JS will be in every one of your bundles--even if you don't specifically import any extra modules. At some point, and usually sooner than later, you should probably make a vendor bundle.

A vendor bundle combines the common code into a shared bundle, allowing the per-app bundles to lose quite a bit of weight. To enable a vendor bundle, do the following:

1. Clear out existing entry and bundle files (see above).
2. Adjust your ``webpack.config.js`` file with a ``chunkFilename`` output and ``optimization`` section.

.. code-block:: js

    module.exports = {
        output: {
            ...
            chunkFilename: 'homepage/scripts/__bundle__.[name].js'
        },
        ...
        optimization: {
            splitChunks: {
                cacheGroups: {
                    vendor: {
                        chunks: 'all',
                        name: 'vendor',
                        test: /[\\/]node_modules[\\/]/,
                        enforce: true,
                    },
                }
            }
        }
    };

The above config creates a single bundle file in ``homepage/scripts/__bundle__.vendor.js``. Any import coming from ``node_modules`` goes into this common bundle.

    The web is filled with exotic recipes for code splitting and even more SO questions regarding splitting bundles into chunks. This configuration is a basic one, and you may want to split the vendor file into more than one chunk. Enter at your own risk...there be dragons here but also some rewards.

3. Recreate the entry files and compile the bundles:

::

    python3 manage.py dmp_webpack --overwrite
    npm run watch

4. Reference your vendor bundle in ``base.htm`` *before* the ``links(self)`` call.

.. code-block:: html+mako

    <script src="/django_mako_plus/dmp-common.js"></script>
    <script src="${STATIC_URL}homepage/scripts/__bundle__.vendor.js"></script>
    ${ django_mako_plus.links(self) }


Bundling: How do I create a single, sitewide bundle?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some situations, it might make sense to create a single monstrosity that includes the scripts for every DMP app on your site.   Let's create a single ``__entry__.js`` file for your entire site

1. Clear out existing entry and bundle files (see above).
2. Modify ``webpack.config.js`` for this single entry.

.. code-block:: js

    module.exports = {
        entry: 'homepage/scripts/__bundle__.js',
        ...
    }

3. Create a single entry file and compile the bundle:

::

    python3 manage.py dmp_webpack --overwrite --single homepage/scripts/__entry__.js
    npm run watch

The above command will place the sitewide entry file in the homepage app, but it could be located anywhere.

4. Specify the bundle as the JS link for all pages:

.. code-block:: python

    'CONTENT_PROVIDERS': [
        { 'provider': 'django_mako_plus.JsContextProvider' },
        { 'provider': 'django_mako_plus.WebpackJsLinkProvider',
          'filepath': 'homepage/scripts/__bundle__.js',
          'duplicates': False,
        },
    ],

The above settings hard code the bundle location for all apps. Since 'duplicates' is False, the bundle will be included once per request, even if your base template (the ``links(self)`` call) is run multiple times by subtemplates.

See also the question (below) regarding creating links manually.


Bundling: How do I create multi-app bundles?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Somewhere in between a sitewide bundle and app-specific bundles lives the multi-app bundle.  Suppose you want app1 and app2 in one bundle and app3, app4, and app5 in another.  The following commands create the two needed entry files:

::

    python3 manage.py dmp_webpack --overwrite --single homepage/scripts/__entry_1__.js app1 app2
    python3 manage.py dmp_webpack --overwrite --single homepage/scripts/__entry_2__.js app3 app4 app5

Then follow the same logic as the previous question (sitewide bundle) to include them in webpack's config and in the provider run.
