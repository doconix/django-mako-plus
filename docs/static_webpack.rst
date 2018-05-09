Bundling with Webpack
================================

    Apologies in advance for the denseness of this page; it bears no relation to the denseness (or lack thereof) of the author.

As you know, DMP automatically creates links for your static files.  When you render ``app/templates/mypage.html``, DMP creates a script tag for ``app/scripts/mypage.js`` and a style tag for ``app/styles/mypage.css``.  This is the default configuration.

Today's production sites generally bundle scripts, styles, and other static assets into combined, optimized files that improve speed and enable better browser caching.  DMP comes with support for bundling with `Webpack <https://webpack.js.org/>`_.

These bundles can be created in at least two ways:

1. A bundle for each app.  If you have four DMP apps, you'll have four bundles.  This approach is described below.
2. A single bundle for your entire site.  If you have four DMP apps, you'll have one bundle.  This approach is described near the end of this document.


Creating Bundles
---------------------------------

Lots of different Javascript files exist in a project.  Some are project-wide, such as ``jQuery``.  Some are full apps, such as ``React`` or ``Vue`` apps.  These generally get bundled in their own ways and don't need DMP's involvement.

DMP-style scripts are coupled with their templates.  They aren't generally self-contained "apps" but add behavior to their templates (although they might start React apps or other components).  When ``mypage.html`` displays, we need ``mypage.js`` to run.

Herein lies the issue that this provider solves: if we bundle several of these scripts together--such as all the scripts in an app--loading the bundle into a page will run not only ``mypage.js``, but also ``otherpage.js`` and ``otherpage2.js`` (assuming these three JS files exist in the same app).  Since the bundle contains scripts for many pages, we need to selectively run a small part of the bundle.

This provider wraps each script inside a function inside the larger bundle.  Since the bundle is a map of template names to functions, the page scripts load but don't run.  When the page is loaded, the ``WebpackJsCallProvider`` runs the appropriate function.

.. image:: _static/webpack.png
   :align: center




The following is the recommended process for creating/using bundles:

1. Create your templates and scripts normally. Templates go in ``yourapp/templates/``.  Scripts go in ``yourapp/scripts/``.
2. If you haven't done so, update your settings file to include a ``WEBPACK_PROVIDERS`` section.  The ``dmp_webpack`` command uses this when generating the entry file.
3. Run ``python3 manage.py dmp_webpack --overwrite``.  This (re)creates an ``appname/scripts/__entry__.js`` file in each of your apps.  This command should be run anytime you create or remove ``.js`` files. It's not necessary when you modify said files.
4. If you haven't done so, run ``npm init`` and create the package.json file.
5. If you haven't done so, create ``webpack.config.js`` in your project root.  In this file, include an entry line for each ``__entry__.js`` file (usually one per app).
6. If developing, run ``npm run dev``; if deploying, run ``npm run build``.  Webpack does its magic and creates ``appname/scripts/__bundle__.js``. Whenever you modify a ``.js`` file, webpack will sense a change in the force and recompile the bundle(s).
7.  If you haven't done so, update your settings file to include two providers in ``CONTENT_PROVIDERS``: ``django_mako_plus.WebpackJsLinkProvider`` and ``django_mako_plus.WebpackJsCallProvider``.  These activate the bundles when browsers load your pages.


Grok Webpack?
~~~~~~~~~~~~~~~~~~~~~~~~

In the discussion below, I'll assume you already understand how to use `npm <https://www.npmjs.com/>`_, `Webpack <https://webpack.js.org/>`_, and their related tools.  If you need to learn more, stop here and go through the tutorials on these technologies.  Set aside a day or three to learn the configuration options, and then come back and continue. :)

Before we begin, be sure ``Node.js`` and ``npm`` are installed and runnable from the command line.  Install webpack (``npm install webpack``).  You should now have a ``node_modules/`` directory in your project.  All of these steps are explained on the `Webpack <https://webpack.js.org/>`_ web site.

The following is an example ``package.json`` file for Webpack 4:

::

    {
    "name": "myproject",
    "version": "1.0.0",
    "scripts": {
        "dev": "webpack --mode development --watch",
        "build": "webpack --mode production"
    }
    }


settings.py
~~~~~~~~~~~~~~~~~~

The following is an example of the settings needed when using bundles:

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {

                # webpack providers - these create the entry files for webpack
                'WEBPACK_PROVIDERS': [
                    { 'provider': 'django_mako_plus.CssLinkProvider' },                              # app/styles/*.css
                    { 'provider': 'django_mako_plus.JsLinkProvider' },                               # app/scripts/*.js
                ],

                # providers - these provide the <link> and <script> tags that the webpack providers make
                'CONTENT_PROVIDERS': [
                    { 'provider': 'django_mako_plus.JsContextProvider' },           # adds the JS context
                    { 'provider': 'django_mako_plus.WebpackCssLinkProvider' },      # <link> tags for CSS bundle
                    { 'provider': 'django_mako_plus.WebpackJsLinkProvider' },       # <script> tags for JS bundle(s)
                    { 'provider': 'django_mako_plus.WebpackJsCallProvider' },       # call the bundle function for the current page
                ],

            }
        }
    ]

Two groups of providers exist above.  ``WEBPACK_PROVIDERS`` is used at development time: it makes the input (entry) files for webpack.  ``CONTENT_PROVIDERS`` is used during the request - it runs at production to create the links in the html.


WEBPACK_PROVIDERS
~~~~~~~~~~~~~~~~~~~~~~~

In the above settings, ``WEBPACK_PROVIDERS`` is used by ``python3 manage.py dmp webpack``, where your ``__entry__.js`` files are generated.  Any providers listed here are used to discover the JS files for your templates.

DMP searches for scripts starting with a template name.  In keeping with this pattern, the ``dmp_webpack`` management command loads each template your apps and includes its script through ``require()``.  The command creates ``app/scripts/__entry__.js`` as an entry point for webpack.  Try running the command on an app that contains several template-related .js files:

::

    python3 manage.py dmp_webpack account --overwrite


The ``--overwrite`` option tells the command to overwrite any existing entry scripts (from an earlier run of the command), and ``account`` tells the command to run only the account app (assuming you have a DMP app by that name, of course).  Once the command finishes, you'll have a file that looks something like this:

::

    (context => {
        DMP_CONTEXT.appBundles["learn/index"] = () => {
            require("./../../homepage/scripts/base.js");
            require("./index.js");
        };
        DMP_CONTEXT.appBundles["learn/support"] = () => {
            require("./../../homepage/scripts/base.js");
        };
        DMP_CONTEXT.appBundles["learn/resource"] = () => {
            require("./../../homepage/scripts/base.js");
            require("./resource.js");
        };
        DMP_CONTEXT.appBundles["learn/course"] = () => {
            require("./../../homepage/scripts/base.js");
            require("./course.js");
        };
        DMP_CONTEXT.appBundles["learn/base_learn"] = () => {
            require("./../../homepage/scripts/base.js");
        };
    })(DMP_CONTEXT.get());

In the above file, the ``learn/index`` page needs two JS files run: ``index.js`` and ``base.js`` (which comes from the homepage app).  Note that even though ``base.js`` is listed many times, webpack will only include it once in the bundle.



Make It So, Bundle One
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the ``__entry__.js`` files are generated, webpack needs to convert them into bundles.  Create a file in your project root called ``webpack.config.js``.  In the following example, I'm assuming you have two DMP apps: ``account`` and ``homepage``:

::

    const path = require('filename');

    module.exports = {
        entry: {
            'account': './account/scripts/__entry__.js',
            'homepage': './homepage/scripts/__entry__.js',
        },
        output: {
            path: path.resolve(__dirname),
            filename: '[name]/scripts/__bundle__.js'
        },
    };

List one entry line for each DMP-enabled app you want bundled.  The entry lines should point to the ``__entry__.js`` files that DMP generated for you.

Now let webpack do its magic!  Run webpack with:

::

    npm run build

When webpack command finishes, you'll have ``__bundle__.js`` files alongside your other scripts.

    You can set the destination to be anywhere you want (such as a ``dist/`` folder), but it's just fine to put them right in your ``app/scripts/`` folder.  DMP only includes **template-related** scripts in ``__entry__.js``, so you won't get infinite bundling recursion by putting the bundle in with the source scripts.


During development time, likely want to run webpack in watch mode so it recompiles the bundles anytime your scripts change:

::

    npm run dev



Including Bundles in your Pages
----------------------------------

Now that the bundles are created, we need to 1) include them with ``<script>`` and ``<link>`` tags, and 2) call the appropriate function(s) within the bundles (based on the template being shown).  This is where ``CONTENT_PROVIDERS`` comes in.

The Link Provider
~~~~~~~~~~~~~~~~~~~~~~~

The ``WebpackJsLinkProvider`` searches for a file matching ``appname/scripts/__bundle__.js`` for each template in the current inheritance.  When it finds a match, a ``<script>`` tag is included in the page.

    Alternatively, you can skip automatic bundle discovery altogether and add ``<script>`` tags to the templates yourself.  This may make sense in some situations, especially if you place these manually-created tags in your base template.


The Function Caller
~~~~~~~~~~~~~~~~~~~~~~~

The second webpack-related provider listed in the ``settings.py`` file above is ``WebpackJsCallProvider``.  This provider runs the appropriate part of the bundle for the current page.  You'll likely want to use this provider even if you do manually include the link tags.

Remember that the bundles contain functions -- one for each page in your app.  These functions *don't* execute when the bundle file is loaded into the browser.  If they did, the JS for every page in your app would run!  Instead, the code for each page is wrapped in a function so it *can* be called when needed.

The ``WebpackJsCallProvider`` looks at the template currently being rendered (and its ancestor templates) and runs the right functions.

An example should make this more clear.  Suppose you have a login template with three levels of inheritance: ``account/templates/login.html``, which inherits from ``account/templates/app_base.htm``, which inherits from ``homepage/templates/base.htm``.  Note that the inheritance crosses two apps (``account`` and ``homepage``).  The following happens:

1. ``WebpackJsLinkProvider`` adds two script tags: the bundle for ``account`` and the bundle for ``homepage``.
2. ``WebpackJsCallProvider`` adds three script calls -- one for each template in the inheritance.

::

    <script data-context="..." src="/static/homepage/scripts/__bundle__.js"></script>
    <script data-context="..." src="/static/account/scripts/__bundle__.js"></script>
    <script data-context="...">
        if (DMP_CONTEXT.appBundles["homepage/base"])    { DMP_CONTEXT.appBundles["homepage/base"]()    };
        if (DMP_CONTEXT.appBundles["account/app_base"]) { DMP_CONTEXT.appBundles["account/app_base"]() };
        if (DMP_CONTEXT.appBundles["account/login"])    { DMP_CONTEXT.appBundles["account/login"]()    };
    </script>

The ``if`` statements are used because the functions are included in the bundle only if a script file for a given page really exists.  In other words, if ``account/scripts/app_base.js`` doesn't exist, the ``account/app_base`` function won't be in the bundle.


Sitewide Bundles
--------------------

If you need the bundles to span across one or more apps, that's possible too.

One Bundle to Rule Them All
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section describes how to create a single monstrosity that includes the scripts for every DMP app on your site.  In some situations, such as sites with a small number of scripts, a single bundle might be more efficient than several app bundles.  To create a single ``__entry__.js`` file for your entire site, run the following:

::

    python3 manage.py dmp_webpack --overwrite --single homepage/scripts/__entry__.js

The above command will place the sitewide entry file in the homepage app, but it could be located anywhere.  Include this single entry file in ``webpack.config.js``.

Since there's only one bundle, you probably don't need the ``WebpackJsLinkProvider`` provider.  Just create a ``<script>`` link in the ``base.htm`` site base template.

When the bundle loads in the browser, the functions for every page will be placed in ``DMP_CONTEXT``.  As described earlier in this document, enable the
``WebpackJsCallProvider`` provider to call the right functions for the current page.


A Few Bundles to Rule Them All
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Somewhere in between a sitewide bundle and app-specific bundles lives the multi-app bundle option.  Suppose you want app1 and app2 in one bundle and app3, app4, and app5 in another.  The following commands create the two needed entry files:

::

    python3 manage.py dmp_webpack --overwrite --single homepage/scripts/__entry_1__.js app1 app2
    python3 manage.py dmp_webpack --overwrite --single homepage/scripts/__entry_2__.js app3 app4 app5



CoffeeScript Example
----------------------------

If you're using Coffee (or TypeScript, or Transpyle, ...), you probably have webpack already up and running.  This example should help explain the specifics for integrating it with DMP scripts.  I'll assume you have both ``*.js`` and ``*.coffee`` files in your ``appname/scripts/`` directories.  The directory structure for the ``account`` app might look like the following:

::

    project/
        account/
            scripts/
                index.coffee
                another.js
            templates/
                index.html

Since they have the same name, the ``index.coffee`` script will be connected with ``index.html`` in our bundle functions.

I'll assume you've installed the npm dependencies with commands like the following:

* ``npm init``
* ``npm install webpack coffeescript coffee-loader``
* Create the ``package.json`` file as described above.
* Create the ``webpack.config.js`` file as described above.

Create a Custom Coffee Provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a provider to find the ``*.coffee`` files in your app directories.  Refer to `custom file locations </static_custom.html>`_ on creating this file.

We'll assume your provider is at ``homepage.lib.providers.WebpackCoffeeProvider``.  It should search for wherever you have your coffee files, such as ``appname/scripts/template.cofee``.


Create the Entry File
~~~~~~~~~~~~~~~~~~~~~~~~

Once your custom coffee provider is alive, add it to your project settings:

::

    'WEBPACK_PROVIDERS': [
        { 'provider': 'django_mako_plus.CssLinkProvider' },             # app/styles/*.css
        { 'provider': 'django_mako_plus.JsLinkProvider' },              # app/scripts/*.js
        { 'provider': 'homepage.lib.providers.WebpackCoffeeProvider' }, # app/scripts/*.coffee
    ],

With this setup, it's valid to have both ``index.coffee`` and ``index.js`` in the scripts directory.  DMP would run both file functions on ``index.html``.

Now create your entry file(s):

::

    python3 manage.py dmp_webpack --overwrite

The above command creates ``account/scripts/__entry__.js``.  In the example output below, the JS files for the ancestor templates (``base.htm``) are also present:

::

    (context => {
        DMP_CONTEXT.appBundles["account/index"] = () => {
            require("./../../homepage/scripts/base.js");
            require("./index.coffee");
        };
    })(DMP_CONTEXT.get());


Create the Bundle
~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure the coffee loader is included in your ``webpack.config.js`` file:

::

    const path = require('path');

    module.exports = {
        devtool: 'source-map',
        entry: {
            'account': './account/scripts/__entry__.js',
        },
        output: {
            path: path.resolve(__dirname),
            filename: '[name]/scripts/__bundle__.js'
        },
        module: {
            rules: [
                {
                    test: /\.coffee$/,
                    use: ['coffee-loader']
                }
            ]
        }
    };

Now create the bundle:

::

    npm run build

During the bundling process, webpack converts the .coffee file to Javascript.  Once ``account/scripts/__bundle__.js`` gets created, you should see the *transpiled* coffee code as well as the base JS.


Link the Bundle
~~~~~~~~~~~~~~~~~~~~~

By production time, webpack has done its work, and the coffee files have been transpiled to JS.  Thereofre, the ``'CONTENT_PROVIDERS'`` listed at the top of this file will work. Just ensure you have them in your settings.
