JS Bundling with Webpack
================================

As you know, DMP automatically creates links for your static files.  When you render ``app/templates/mypage.html``, DMP creates a script tag for ``app/scripts/mypage.js`` and a style tag for ``app/styles/mypage.css``.  This is the default configuration.

Today's production sites generally bundle scripts, styles, and other static assets into combined, optimized files that improve speed and enable better browser caching.  DMP comes with support for bundling with `Webpack <https://webpack.js.org/>`_.

Philosophy
---------------

Lots of different Javascript files exist in a project.  Some are project-wide, such as ``jQuery``).  Some are full apps, such as ``React`` or ``Vue`` apps.  These generally get bundled in their own ways and don't need DMP's involvement.

DMP-style scripts are intricately coupled with their templates.  They aren't generally self-contained "apps" but add behavior to their templates (although they can start things like React apps).  When ``mypage.html`` displays, we need ``mypage.js`` to run.  It wouldn't make sense to run ``otherpage.js``.

If we bundle several of these scripts together--such as all the scripts in an app--they'll all run on every page in the app.  Even if we bundle all the files in ``app/scripts/*.js`` together, we still need just one of them to run.

The goal of this provider is to place all the scripts for an app in a single file, but wrap each script inside a function.  Since each page script is a function in the bundle, it loads but doesn't run.  A controller script, named ``__entry__.js``, checks the ``DMP_CONTEXT`` for the current template's script (the "page function" in the bundle), and runs the appropriate function.

This pattern allows us to have a single ``__bundle__.js`` file for an app that can be cached by the browser.  As the user navigates to different pages in the app, the controller script runs the right code.  It also minifies and compresses better than separate files.

.. image:: _static/webpack.png
   :align: center


Grok Webpack?
-------------------

In the discussion below, I'll assume you already understand how to use `npm <https://www.npmjs.com/>`_, `Webpack <https://webpack.js.org/>`_, and their related tools.  If you need to learn more, stop here and go through the tutorials on these technologies.  Set aside a day or three to learn the configuration options. :)

Before we begin, be sure ``Node.js`` and ``npm`` are installed and runnable from the command line.  Install webpack (``npm install webpack``).  You should now have a ``node_modules/`` directory in your project.

Additionally, be sure your ``package.json`` file contains an entry to build with webpack: ``"scripts": { "build": "webpack" }``.


Entry File
---------------------------

In DMP, searching for scripts starts with the template name.  In keeping with this pattern, the ``dmp_webpack`` management command loads each template your apps and includes its script through ``require()``.  The command creates ``app/scripts/__entry__.js`` as an entry point for webpack.  Try running the command on an app that contains several template-related .js files:

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

Create a file in your project root called ``webpack.config.js``.  In the following example, I'm assuming you have two DMP apps: ``account`` and ``homepage``:

::

    const path = require('path');

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

List one entry line for each DMP-enabled app you want bundled.  If you skipped ahead in the reading, remember that DMP created ``__entry__.js`` (you don't have to).

At this point, let webpack do its work!  Run webpack with:

::

    npm run build

You should now have ``__bundle__.js`` files alongside your other scripts.

    You can set the destination to be anywhere you want (such as a ``dist/`` folder), but it's just fine to put them right in your ``app/scripts/`` folder.  DMP only includes **template-related** scripts in ``__entry__.js``, so you won't get infinite bundling recursion by putting the bundle in with the scripts.


Script Tag
-------------------

We now have our bundle created, but it still needs a ``<script>`` tag to load on pages.  If your bundle is part of a larger distribution plan, feel free to include the bundle that way.  Be sure to call the right page function.

DMP is also capable of creating the link and calling the page function as part of the static links process.  Simply include the following provider in your `list of providers <static_providers.html>`_:

::

    'provider': 'django_mako_plus.AppJsBundleProvider',
    'path': '{appname}/scripts/__bundle__.js',

When a template is rendered, DMP will look the bundle using the ``path`` above.  If a match is found, DMP prints 1) a ``<script>`` tag to load the bundle, and 2) an inline script to call the right function for the page being rendered.  Since ``AppJsBundleProvider`` is a normal provider, this all happens during the ``${ django_mako_plus.links() }`` call you have on your site base template.