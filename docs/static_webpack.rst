Webpack
================

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




Tutorial
---------------------------------

Let's create a "normal" Django/DMP project and then convert it to a "bundle-endabled" Django/DMP project.

    A note before continuing: JS bundling can be difficult for Python developers at first because it's based in fundamentally different thinking than the Python world is. Python compiles .py files to .pyc, but otherwise keeps the source structure at runtime. Bundling requires setting up npm, ``node_modules``, and multiple config files. As of 2018, Javascript's import landscape is a battleground of similar-looking but quite different standards and libraries: <script src=>, jQuery plugins, CommonJS,AMD, RequireJS, npm, yarn, ES6 import standards, and dynamic imports. For Python devs who are used to a benevolent dictator solving divisive issues (like Guido did with the ``m if x else n`` debate), the chaotic and evolving JS ecosystem can be overwhelming. If you are new to bundling, take the time to read the documentation on ``npm`` and ``webpack`` and create a small Node JS web site.

Create a DMP project
~~~~~~~~~~~~~~~~~~~~~~~~

The installation steps for DMP are given elsewhere in these documents, so `take a detour if you need detailed instructions </install_new.html>`_. Here's a review for those need a quick summary:

::

    pip3 install --upgrade django-mako-plus
    python3 -m django_mako_plus dmp_startproject mysite
    cd mysite
    python3 manage.py migrate
    python3 manage.py createsuperuser
    python3 manage.py dmp_startapp homepage
    # Finally, open settings.py and add "homepage" to your INSTALLED_APPS

Run your project, and ensure the "Welcome to DMP" page comes up. If not, head over to the DMP installation pages for ideas.

Note that your new project already contains ``homepage/scripts/index.js``. Let's add another script file so we can see the bundling work:

.. code:: javascript

    // homepage/scripts/base.js:
    (function(context) {
        console.log('In base.js!')
    })(DMP_CONTEXT.get());

You should now have two JS files: ``index.js`` and ``base.js``. Since template ``index.html`` extends template ``base.html``, both JS files should run when we view ``index.html``. Refresh your project home page and check the JS console (right-click the page, then Inspect Element) for the output of both scripts.


Initialize Node
~~~~~~~~~~~~~~~~~~~~~~~~~~

Install Node from `https://nodejs.org <https://nodejs.org/>`_. After installation, open a terminal and ensure you can run ``npm`` from the command line.

::

    npm --version

Initialize the npm repository and install webpack. When asked, just accept the defaults for package name, version, etc.

::

    # run from your project root (mysite):
    npm init
    npm install --save-dev webpack webpack-cli style-loader css-loader
    # if using git, add "node_modules/" to your .gitignore file


The above commands changed your project a little:

1. The ``node_modules`` directory exists in your project root and contains dozens of Javascript packages, including core Node packages and webpack-related dependencies. This directory is the Javascript equivalent to ``pip3``, a virtual environment, and python site-packages. This directory can be recreated anytime by running ``npm install``.
2. The ``package.json`` file in your project root contains a list of npm package dependencies. If you open the file, you'll notice that ``webpack`` is listed as a development dependency (it isn't needed at production, so it's in "devDependencies").

Let's create some shortcut comands to make running webpack easier. These are defined in ``package.json`` under the ``scripts`` key, like this:

.. code:: javascript

    {
        ...,
        "scripts": {
            "watch": "webpack --mode development --watch",
            "build": "webpack --mode production"
        }
    }

The above two scripts can be run with ``npm run watch`` and ``npm run build``, but we're not quite ready to run them yet. So hold up, Tex.


Create the Entry File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Webpack requires one or more "entry" files as starting points for its bundles. In Node applications and single-page webapps, a "main" JS file runs everything. Multi-page, Django-style web sites are different: each page is essentially an "app" that requires a new bundle.

That means our Django/DMP projects have **lots of entry points**: the login page, password change page, user information page, and so forth. We don't really have an "entry" page to point webpack at.

That's where DMP comes in. DMP understands your project structure, including how ``templates``, ``scripts``, and ``styles`` directories are connected. DMP will create ``homepage/scripts/__entry__.js`` as the "entry" file for our ``homepage`` app.

Run the following to create the ``__entry__.js`` file:

::

    python3 manage.py dmp_webpack --overwrite

When the command finishes, you'll have a new file, ``homepage/scripts/__entry__.js``, that points to the scripts and styles in the app. Check out the file to see what DMP created.

Now that you've seen the result, let's detail the discovery process that just occurred:

--------

**First, DMP deep searched the templates directory ``homepage/templates/`` for all files (except those starting with double-underscores, like ``__dmpcache__``.** DMP found three files:

::

    homepage/templates/base_ajax.htm
    homepage/templates/base.htm
    homepage/templates/index.html

--------

**Next, DMP loaded each file as a template object (as if it were about to be rendered) and ran its `Providers </static_providers.html>`_, ``CssLinkProvider`` and ``JsLinkProvider``.**  These two providers are the defaults, but you can `customize them in settings.py </basics_settings.html>`_ (see ``WEBPACK_PROVIDERS``).

Now, providers are built to discover the script and style files that are associated with templates, so DMP used them to find the files needed for our bundle:

::

    homepage/templates/base_ajax.htm    # has no scripts or styles, so DMP skips it
    homepage/templates/base.htm         # DMP finds base.js and base.css
    homepage/templates/index.html       # DMP finds index.js and index.css

The providers yielded four files, shown here as a list relative to the entry file path:

.. code:: python

    [ "./base.js", "../styles/base.css", "./index.js", "../styles/index.css" ]

--------

**Finally, DMP created ``homepage/scripts/__entry__.js``, which we'll use later as Webpack's entry point.** This file contains a number of Node ``require`` statements:

.. code:: javascript

    (context => {
        DMP_CONTEXT.appBundles["homepage/index"] = () => {
            require("./base.js");
            require("./index.js");
            require("./../styles/base.css");
            require("./../styles/index.css");
        };
        DMP_CONTEXT.appBundles["homepage/base"] = () => {
            require("./base.js");
            require("./../styles/base.css");
        };
    })(DMP_CONTEXT.get());




Configure and Run Webpack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We need to tell webpack to start with our entry file. Create a file in your project root called ``webpack.config.js``:

.. code:: javascript

    const path = require('path');

    module.exports = {
        entry: {
            'homepage': './homepage/scripts/__entry__.js',
        },
        output: {
            path: path.resolve(__dirname),
            filename: '[name]/scripts/__bundle__.js'
        },
    };

The above config defines just one entry point because this tutorial has only one app. For a bigger projects you'd list each app in "entry" section. The "output" section would be the same.

    You can set the destination to be anywhere you want (such as a ``dist/`` folder), but it's just fine to put them right in your ``app/scripts/`` folder.  DMP only includes **template-related** scripts in ``__entry__.js``, so you won't get infinite bundling recursion by putting the bundle in with the source scripts.

Let's run webpack in development (watch) mode. After creating our initial bundle, webpack continues watching the linked files for changes. Whenever we change the entry file, script files, or style files, webpack recreates the bundle automatically. Run the following:

::

    npm run watch

Assuming webpack runs successfully, you now have ``homepage/scripts/__bundle__.js``. Scan/search the file for the JS and CSS content that was bundled.


Include the Bundle in Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As you learned in other sections, DMP automatically creates ``<script>`` and ``<style>`` links in your html templates. In our project, this magic happens during the call to ``${ django_mako_plus.links(self) }`` in ``base.htm`` (which ``index.html`` extends from). For example, the template ``homepage/templates/index.html`` directs the Providers to find and link ``homepage/scripts/index.js`` and ``homepage/styles/index.css``.

We need swap these Providers with ones that find and link ``homepage/scripts/__bundle__.js``. This is done by setting ``CONTENT_PROVIDERS`` in ``settings.py``:

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                # providers - these provide the <link> and <script> tags that the webpack providers make
                'CONTENT_PROVIDERS': [
                    { 'provider': 'django_mako_plus.JsContextProvider' },
                    { 'provider': 'django_mako_plus.WebpackJsLinkProvider' },
                    { 'provider': 'django_mako_plus.WebpackJsCallProvider' },
                ],
            }
        }
    ]

These new Providers give the following behavior:

1. ``JsContextProvider`` is the same as before. `It sets values from the view into the JS context </static_context.html>`_.
2. ``WebpackJsLinkProvider`` creates the link for the bundle: ``<script src="/static/homepage/scripts/__bundle__.js">``.
3. ``WebpackJsCallProvider`` calls the function(s) appropriate to the current template being shown.

    Regarding #2, you can `change the default paths in settings.py </basics_settings.html>`_. Just be sure to match the webpack config path with the link provider path.

    Regarding #3, you could remove this provider and instead add ``<script>`` tags to the templates yourself.  This may make sense in situations like site-wide bundles.


Test It!
~~~~~~~~~~~~~~~~

We've configured webpack, created the entry file and output bundle, and set DMP to link correctly. The only thing remaining is to run the Django server and see the benefits of your work!

::

    python3 manage.py runserver
    # take a browser to http://localhost:8000

Be sure to check the following:

* Right-click and Inspect to view the JS console. The messages in our .js files and/or any errors will show there.
* Also in the inspector, check out the CSS rules (which are now coming from the bundle).
* Right-click and view the page source. You'll see the links that DMP created. If you see the old ``<script>`` and ``<style>`` links, check your settings file.


Building for Production
---------------------------

To create a production bundle, issue webpack a build command:

::

    npm run build

If you look at the generated bundle file, you'll find it is minified and ready for deployment.


Small vs. Large Bundles
------------------------------------

By default, DMP builds standalone, independent bundles that don't have dependenices on other apps. This is the most reliable way to use bundles (hence the default method), but it can generate larger bundles than are actually needed. Read on to slim down the bundles through reuse and cross-bundle calls.

    This only matters in multi-app projects where multiple bundles are being generated. Single-app projects (such as this tutorial) only create one bundle.

Suppose we have a project with two apps, with the following partial structure:

::

    mysite/
        account/
            styles/
                login.css
            scripts/
                login.js
            templates/
                login.html (inherits from base.html: <%inherit file="/homepage/templates/base.htm"/>)
        homepage/
            styles/
                base.css
                index.css
            scripts/
                base.js
                index.js (inherits from base.html: <%inherit file="base.htm"/>)
            templates/
                base.html
                index.html

The following table shows how this structure would be rendered in 1) regular, unbundled DMP, 2) standalone, bundled DMP (the default when bundling), and 3) dependent, bundled DMP.

+-----------------------+---------------------------------------------------------------------------+-----------------------------------------------------------------+
| URL                   | Regular, Unbundled DMP                                                    | Standalone, Bundled DMP (larger bundles)                        |
+=======================+===========================================================================+=================================================================+
| ``/account/login/``   | .. code-block:: html                                                      | .. code-block:: html                                            |
|                       |    :caption: Generated by links() call:                                   |     :caption: /account/scripts/__entry__.js:                    |
|                       |                                                                           |                                                                 |
|                       |    <link type="text/css" href="/static/homepage/styles/base.css" />       |     (context => {                                               |
|                       |    <link type="text/css" href="/static/account/styles/login.css" />       |         DMP_CONTEXT.appBundles["account/base_app"] = () => {    |
|                       |    <script src="/static/account/scripts/base.js"></script>                |             require("./../../homepage/styles/base.css");        |
|                       |    <script src="/static/account/scripts/login.js"></script>               |         };                                                      |
|                       |                                                                           |         DMP_CONTEXT.appBundles["account/login"] = () => {       |
|                       |                                                                           |             require("./../../homepage/styles/base.css");        |
|                       |                                                                           |             require("./../styles/login.css");                   |
|                       |                                                                           |             require("./login.js");                              |
|                       |                                                                           |         };                                                      |
|                       |                                                                           |         DMP_CONTEXT.appBundles["account/password"] = () => {    |
|                       |                                                                           |             require("./../../homepage/styles/base.css");        |
|                       |                                                                           |         };                                                      |
|                       |                                                                           |     })(DMP_CONTEXT.get());                                      |
|                       |                                                                           |                                                                 |
|                       |                                                                           |                                                                 |
|                       |                                                                           |                                                                 |
|                       |                                                                           |                                                                 |
|                       |                                                                           |                                                                 |
+-----------------------+---------------------------------------------------------------------------+-----------------------------------------------------------------+



Sitewide Bundles
--------------------

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
