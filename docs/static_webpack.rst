JS Bundling with Webpack
================================

    This is an advanced topic, which means you'll see a lot of red code on this page.  Apologies in advance for the denseness of some of this.  It bears no relation to the denseness (or lack thereof) of the author.

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


Workflow
-------------------

The following is an overview of the development workflow.  The details of each step are given lower in this document.

1. Development:
    a. Create your templates and scripts normally. Templates go in ``yourapp/templates/``.  Scripts go in ``yourapp/scripts/``.
    b. During development, you can use the normal providers (no bundles needed).
2. Deployment:
    a. If you haven't done so, update your settings file to include a ``WEBPACK_PROVIDERS`` section.  The ``dmp__webpack`` command uses this to find your scripts.
    b. When you are ready to deploy, run ``python manage.py dmp_webpack --overwrite``.  This (re)creates ``appname/scripts/__entry__.js`` in each of your apps.
    c. If you haven't done so, create ``webpack.config.js`` in your project root.  In this file, include an entry line for each of the ``__entry__.js`` files in your apps.
    d. Run ``npm run build``.  Webpack does its magic and creates ``appname/scripts/__bundle__.js``.
    e. Continue deployment normally: collect your static files and upload to your server.
3. Production:
    a. Ensure your production settings file doesn't list the ``JsLinkProvider`` provider.
    b. Ensure your production settings file DOES list the ``WebpackJsLinkProvider`` provider, which adds the ``<script>`` link(s) to the appropriate bundle files for the current template and its supertemplates.
    c. As an alternative to the last step (b), you can include the ``<script>`` tag manually (such as listing it in an app-specific or site-wide base template).
    d. Ensure your production settings file DOES list the ``WebpackJsCallProvider`` provider, which makes the ``yourapp/template()`` function call.  This runs the small part of the bundle that pertains to the template (and its supertemplates) currently being viewed.

In your settings file, set ``"enabled": settings.DEBUG`` on providers that should run only during development and ``"enabled": not settings.DEBUG`` on providers that should run only at production.


Grok Webpack?
-------------------

In the discussion below, I'll assume you already understand how to use `npm <https://www.npmjs.com/>`_, `Webpack <https://webpack.js.org/>`_, and their related tools.  If you need to learn more, stop here and go through the tutorials on these technologies.  Set aside a day or three to learn the configuration options, and then come back and continue. :)

Before we begin, be sure ``Node.js`` and ``npm`` are installed and runnable from the command line.  Install webpack (``npm install webpack``).  You should now have a ``node_modules/`` directory in your project.

Additionally, be sure your ``package.json`` file contains an entry to build with webpack: ``"scripts": { "build": "webpack" }``.

All of these steps are explained on the `Webpack <https://webpack.js.org/>`_ web site.


settings.py
------------------------

The following is an example of the settings needed when using bundles.  Note that the example only lists the JS-related providers.  It doesn't include the providers for CSS that would normally be there as well.

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                # these define how page scripts are run by browsers
                'CONTENT_PROVIDERS': [
                    {
                        'provider': 'django_mako_plus.JsContextProvider',
                    },
                    {
                        'provider': 'django_mako_plus.JsLinkProvider',
                        'enabled': ns.DEBUG,      # DEVELOPMENT only
                    },
                    {
                        'provider': 'django_mako_plus.WebpackJsLinkProvider',
                        'filename': lambda pr: os.path.join(*flatten(pr.app_config.path, 'scripts', '__bundle__.js')),
                        'enabled': not ns.DEBUG,  # PRODUCTION only
                    },
                    {
                        'provider': 'django_mako_plus.WebpackJsCallProvider',
                        'enabled': not ns.DEBUG,  # PRODUCTION only
                    },
                ],
                # these are using during a `python manage.py dmp_webpack` run - these are the ones you should customize (if desired)
                # the JS files found by these providers are the ones placed in __entry__.js
                # the providers listed here should extend django_mako_plus.LinkProvider
                'WEBPACK_PROVIDERS': [
                    { 'provider': 'django_mako_plus.JsLinkProvider' },       # generates links for app/scripts/template.js
                ],
            }
        }
    ]


CONTENT_PROVIDERS
~~~~~~~~~~~~~~~~~~~~~

The ``CONTENT_PROVIDERS`` setting is used to find scripts during the normal running of your servers.  The ``JsContextProvider``, which brings variables from your Python context to the JS closures, is active at all times.

During development, DMP's normal ``JsLinkProvider`` is used so bundles don't have to be built every time you make a change to a script.  Note the use of ``enabled`` to ensure it activates only at development time.

At production, the ``WebpackJsLinkProvider`` finds ``appname/scripts/__bundle__.js`` files.  It generates ``<script>`` links for the template (and supertemplate) being rendered.  If you need to customize the location, the ``filename`` gives a function (note the ``lambda``) that returns the filename to be searched for.  If defined as a function instead of a lambda, it would look like this:

::

    def get_bundle_filename(pr):
        return 'bundle path and filename to search for'

The ``pr`` parameter is a subclass of ``django_mako_plus.provider.base.BaseProvider``. It contains information that can be useful in constructing the filename:

* ``pr.app_config``: The AppConfig for the current template's app.
* ``pr.template_file``: The current template's filename.
* ``pr.subdir``: The current template's directory.
* ``pr.template_name``: The name of the current template (filename sans the extension).
* ``pr.options``: The options dictionary from settings for this provider (plus any default options not specified in settings).

WEBPACK_PROVIDERS
~~~~~~~~~~~~~~~~~~~~~~~

The ``WEBPACK_PROVIDERS`` setting is used during the call to ``python manage.py dmp_webpack``, where your ``__entry__.js`` files are generated.  The providers listed here are used to discover the JS files for your templates.

DMP searches for scripts starting with a template name.  In keeping with this pattern, the ``dmp_webpack`` management command loads each template your apps and includes its script through ``require()``.  The command creates ``app/scripts/__entry__.js`` as an entry point for webpack.  Try running the command on an app that contains several template-related .js files:

::

    python3 manage.py dmp_webpack account --overwrite


The ``--overwrite`` option tells the command to overwrite any existing entry scripts (from an earlier run of the command), and ``account`` tells the command to run only the account app (assuming you have a DMP app by that name, of course).  Once the command finishes, you'll have a file that looks something like this:

::

    (context => {
        DMP_CONTEXT.appBundles["learn/index"] = () => { require("./../../homepage/scripts/base_site.js"); require("./index.js"); };
        DMP_CONTEXT.appBundles["learn/support"] = () => { require("./../../homepage/scripts/base_site.js"); };
        DMP_CONTEXT.appBundles["learn/resource"] = () => { require("./../../homepage/scripts/base_site.js"); require("./resource.js"); };
        DMP_CONTEXT.appBundles["learn/course"] = () => { require("./../../homepage/scripts/base_site.js"); require("./course.js"); };
        DMP_CONTEXT.appBundles["learn/base_learn"] = () => { require("./../../homepage/scripts/base_site.js"); };
    })(DMP_CONTEXT.get());

In the above file, the ``learn/index`` page needs two JS files run: ``index.js`` and ``base_site.js`` (which comes from the homepage app).  Note that even though ``base_site.js`` is listed many times, webpack will only include it once in the bundle.


Make It So, Bundle One
--------------------------------------

Once the ``__entry__.js`` files are generated by DMP, we need webpack to convert them into bundles.  Create a file in your project root called ``webpack.config.js``.  In the following example, I'm assuming you have two DMP apps: ``account`` and ``homepage``:

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


Including Bundles in your Pages
----------------------------------

Now that the bundles are created, we need to 1) include them with ``<script>`` tags, and 2) call the appropriate function(s) within the bundles (based on the template being shown).

The first method of including the ``<script>`` tags is enabling ``WebpackJsLinkProvider`` in ``CONTENT_PROVIDERS`` in settings.  During the call to ``${ django_mako_plus.links() }``, this provider will include the bundle for the template being rendered.  It will further include additional bundles for supertemplates that the template inherits from (if they are located in other apps).

The second method of including the ``<script>`` tags is to place them in base templates, such as ``base.htm`` or an app-specific ``app_base.htm``.  If your templates all inherit from these common templates, the script tags will be placed on the appropriate pages.

Remember that the bundles contain functions--one per page.  When the bundles are run, the functions are placed in ``window.DMP_CONTEXT``.  The ``WebpackJsCallProvider`` provider does this for you.  It should always come after ``WebpackJsLinkProvider`` so the script functions get loaded first.

Suppose you have a login template with three levels of inheritance: ``account/templates/login.html``, which inherits from ``account/templates/app_base.htm``, which inherits from ``homepage/templates/base.htm``.  Note that the inheritance crosses two apps (``account`` and ``homepage``).  The following happens:

1. ``WebpackJsLinkProvider`` includes two script tags: the bundle for ``account`` and the bundle for ``homepage``.
2. ``WebpackJsCallProvider`` includes the following in your rendered html page:

::

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
                    {
                        'provider': 'django_mako_plus.WebpackJsLinkProvider',
                        'filename': get_bundle_filename,
                    },
            }
        }
    ]

Note that the function is run once per template -- the first time a template is accessed.  During production, the filename is memoized after the first render of a template.  This means slow functions are fine here, but it also means you can't return something different on each render.
