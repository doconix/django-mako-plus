JS Bundling with Webpack
================================

    Apologies in advance for the denseness of this page; it bears no relation to the denseness (or lack thereof) of the author.

As you know, DMP automatically creates links for your static files.  When you render ``app/templates/mypage.html``, DMP creates a script tag for ``app/scripts/mypage.js`` and a style tag for ``app/styles/mypage.css``.  This is the default configuration.

Today's production sites generally bundle scripts, styles, and other static assets into combined, optimized files that improve speed and enable better browser caching.  DMP comes with support for bundling with `Webpack <https://webpack.js.org/>`_.

These bundles can be created in at least two ways:

1. A bundle for each app.  If you have four DMP apps, you'll have four bundles.  This approach is described below.
2. A single bundle for your entire site.  If you have four DMP apps, you'll have one bundle.  This approach is described near the end of this document.

Philosophy
---------------

Lots of different Javascript files exist in a project.  Some are project-wide, such as ``jQuery``.  Some are full apps, such as ``React`` or ``Vue`` apps.  These generally get bundled in their own ways and don't need DMP's involvement.

DMP-style scripts are coupled with their templates.  They aren't generally self-contained "apps" but add behavior to their templates (although they might start React apps or other components).  When ``mypage.html`` displays, we need ``mypage.js`` to run.

Herein lies the issue that this provider solves: if we bundle several of these scripts together--such as all the scripts in an app--loading the bundle into a page will run not only ``mypage.js``, but also ``otherpage.js`` and ``otherpage2.js`` (assuming these three JS files exist in the same app).  Since the bundle contains scripts for many pages, we need to selectively run a small part of the bundle.

This provider wraps each script inside a function inside the larger bundle.  Since the bundle is a map of template names to functions, the page scripts load but don't run.  When the page is loaded, the ``WebpackJsCallProvider`` runs the appropriate function.

.. image:: _static/webpack.png
   :align: center


Overview
-------------------

First we'll present an overview of the process.  Note that some steps only work correctly once you've continued through the setup in this document.

1. Create your templates and scripts normally. Templates go in ``yourapp/templates/``.  Scripts go in ``yourapp/scripts/``.
2. If you haven't done so, update your settings file to include a ``WEBPACK_PROVIDERS`` section.  The ``dmp_webpack`` command uses this when generating the entry file.
3. Run ``python manage.py dmp_webpack --overwrite``.  This (re)creates an ``appname/scripts/__entry__.js`` file in each of your apps.  This command should be run anytime you create or remove ``.js`` files. It's not necessary when you modify said files.
4. If you haven't done so, run ``npm init`` and create the package.json file.
5. If you haven't done so, create ``webpack.config.js`` in your project root.  In this file, include an entry line for each ``__entry__.js`` file (usually one per app).
6. If developing, run ``npm run dev``; if deploying, run ``npm run build``.  Webpack does its magic and creates ``appname/scripts/__bundle__.js``. Whenever you modify a ``.js`` file, webpack will sense a change in the force and recompile the bundle(s).
7.  If you haven't done so, update your settings file to include two providers in ``CONTENT_PROVIDERS``: ``django_mako_plus.WebpackJsLinkProvider`` and ``django_mako_plus.WebpackJsCallProvider``.  These activate the bundles when browsers load your pages.


Grok Webpack?
-------------------

In the discussion below, I'll assume you already understand how to use `npm <https://www.npmjs.com/>`_, `Webpack <https://webpack.js.org/>`_, and their related tools.  If you need to learn more, stop here and go through the tutorials on these technologies.  Set aside a day or three to learn the configuration options, and then come back and continue. :)

Before we begin, be sure ``Node.js`` and ``npm`` are installed and runnable from the command line.  Install webpack (``npm install webpack``).  You should now have a ``node_modules/`` directory in your project.  All of these steps are explained on the `Webpack <https://webpack.js.org/>`_ web site.

The following is an example ``package.json`` file for Webpack 4:

{
  "name": "myproject",
  "version": "1.0.0",
  "scripts": {
    "dev": "webpack --mode development --watch",
    "build": "webpack --mode production"
  }
}


settings.py
------------------------

The following is an example of the settings needed when using bundles.  Note that the example is limited to the bundle-related providers -- you'll likely have additional providers for things like CSS files.

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                # these define how page scripts are run by browsers
                'CONTENT_PROVIDERS': [
                    # injects jscontext-tagged context variables into JS
                    { 'provider': 'django_mako_plus.JsContextProvider' },

                    # <script> tags for the JS bundle file(s); filename can be a function (like below) or a string
                    # if your base template hard codes a link to the bundle(s), you don't need this
                    { 'provider': 'django_mako_plus.WebpackJsLinkProvider',
                        'filename': lambda pr: os.path.join(pr.app_config.path, 'scripts', '__bundle__.js')
                    },

                    # calls the appropriate bundle functions for the current page
                    { 'provider': 'django_mako_plus.WebpackJsCallProvider' },
                ],

                # these are using during a `python manage.py dmp_webpack` run - these are the ones you should customize (if desired)
                # the JS files found by these providers are the ones placed in __entry__.js
                # the providers listed here should extend django_mako_plus.LinkProvider
                'WEBPACK_PROVIDERS': [
                    { 'provider': 'django_mako_plus.JsLinkProvider' },
                ],
            }
        }
    ]


WEBPACK_PROVIDERS
~~~~~~~~~~~~~~~~~~~~~~~

In the above settings, ``WEBPACK_PROVIDERS`` is used by ``python manage.py dmp_webpack``, where your ``__entry__.js`` files are generated.  Any providers listed here are used to discover the JS files for your templates.

DMP searches for scripts starting with a template name.  In keeping with this pattern, the ``dmp_webpack`` management command loads each template your apps and includes its script through ``require()``.  The command creates ``app/scripts/__entry__.js`` as an entry point for webpack.  Try running the command on an app that contains several template-related .js files:

::

    python3 manage.py dmp_webpack account --overwrite


The ``--overwrite`` option tells the command to overwrite any existing entry scripts (from an earlier run of the command), and ``account`` tells the command to run only the account app (assuming you have a DMP app by that name, of course).  Once the command finishes, you'll have a file that looks something like this:

::

    (context => {
        DMP_CONTEXT.appBundles["learn/index"] = () => { require("./../../homepage/scripts/base.js"); require("./index.js"); };
        DMP_CONTEXT.appBundles["learn/support"] = () => { require("./../../homepage/scripts/base.js"); };
        DMP_CONTEXT.appBundles["learn/resource"] = () => { require("./../../homepage/scripts/base.js"); require("./resource.js"); };
        DMP_CONTEXT.appBundles["learn/course"] = () => { require("./../../homepage/scripts/base.js"); require("./course.js"); };
        DMP_CONTEXT.appBundles["learn/base_learn"] = () => { require("./../../homepage/scripts/base.js"); };
    })(DMP_CONTEXT.get());

In the above file, the ``learn/index`` page needs two JS files run: ``index.js`` and ``base.js`` (which comes from the homepage app).  Note that even though ``base.js`` is listed many times, webpack will only include it once in the bundle.



Make It So, Bundle One
--------------------------------------

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

Now that the bundles are created, we need to 1) include them with ``<script>`` tags, and 2) call the appropriate function(s) within the bundles (based on the template being shown).  This is where ``CONTENT_PROVIDERS`` comes in.  Refer back to the ``settings.py`` example in the section above as your read this section.

The Link Provider
~~~~~~~~~~~~~~~~~~~~~~~

The ``WebpackJsLinkProvider`` searches for a file matching ``appname/scripts/__bundle__.js`` for each template in the current inheritance.  When it finds a match, a ``<script>`` tag is included in the page.

    Alternatively, you can skip automatic bundle discovery altogether and add ``<script>`` tags to the templates yourself.  This may make sense in some situations, especially if you place these manually-created tags in your base template.

If you need to customize the location, the ``filename`` can be specified as a string OR as a function/lambda.  The following is an example:

::

    def get_bundle_filename(pr):
        return os.path.join(settings.BASE_DIR, pr.app_config.name, 'bundle path and filename')

The ``pr`` parameter is a subclass of ``django_mako_plus.provider.base.BaseProvider``. It contains information that can be useful in constructing the filename:

* ``pr.app_config``: The AppConfig for the current template's app.
* ``pr.template_file``: The current template's filename.
* ``pr.subdir``: The current template's directory.
* ``pr.template_name``: The name of the current template (filename sans the extension).
* ``pr.options``: The options dictionary from settings for this provider (plus any default options not specified in settings).


The Function Caller
~~~~~~~~~~~~~~~~~~~~~~~

The second webpack-related provider listed in the ``settings.py`` file above is ``WebpackJsCallProvider``.  This provider runs the appropriate part of the bundle for the current page.  You'll likely want to use this provider whether you auto-discover or manually code the script tags.

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


One Bundle to Rule Them All
---------------------------------

This section describes how to create a single monstrosity that includes the scripts for every DMP app on your site.  In some situations, such as sites with a small number of scripts, a single bundle might be more efficient than several app bundles.  To create a single ``__entry__.js`` file for your entire site, run the following:

::

    python manage.py dmp_webpack --overwrite --single homepage/scripts/__entry__.js

The above command will place the sitewide entry file in the homepage app, but it could be located anywhere.  Include this single entry file in ``webpack.config.js``.

Since there's only one bundle, you probably don't need the ``WebpackJsLinkProvider`` provider.  Just create a ``<script>`` link in the ``base.htm`` site base template.

When the bundle loads in the browser, the functions for every page will be placed in ``DMP_CONTEXT``.  As described earlier in this document, enable the
``WebpackJsCallProvider`` provider to call the right functions for the current page.


A Few Bundles to Rule Them All
----------------------------------

Somewhere in between a sitewide bundle and app-specific bundles lives the multi-app bundle option.  Suppose you want app1 and app2 in one bundle and app3, app4, and app5 in another.  The following commands create the two needed entry files:

::

    python manage.py dmp_webpack --overwrite --single homepage/scripts/__entry_1__.js app1 app2
    python manage.py dmp_webpack --overwrite --single homepage/scripts/__entry_2__.js app3 app4 app5

To include the ``<script>`` tag for these bundles, use something like the following function in your settings file:

::

    def get_bundle_filename(provider):
        if provider.app_config.name in ( 'app1', 'app2' ):
            return '/path/to/__bundle_1_.js'
        return '/path/to/__bundle_2_.js'

    TEMPLATES = [
        {
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    { 'provider': 'django_mako_plus.WebpackJsLinkProvider', 'filename': get_bundle_filename },
                    { 'provider': 'django_mako_plus.WebpackJsCallProvider' },
            }
        }
    ]

Note that the function is run once per template -- the first time a template is accessed.  During production, the filename is memoized after the first render of a template.  This means slow functions are fine here, but it also means you can't return something different on each render.
