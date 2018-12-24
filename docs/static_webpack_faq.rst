Webpack FAQ
================

If you haven't read `the DMP Webpack documentation </static_webpack.html>`_, please do so before reading this FAQ.

How do I clear the generated bundle files?
-------------------------------------------------

In a terminal (Mac, Linux, or Windows+GitBash), issue these commands:

::

    # careful, this is recursive!
    rm **/__entry__.js
    rm **/__bundle__.js



How do I use Sass (Less, TypeScript, etc.) with DMP Webpack?
--------------------------------------------------------------

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



How do I create a vendor bundle?
-----------------------------------

In the `tutorial </static_webpack.html>`_, we created one bundle per app.  These bundles can grow large as you enjoy the convenience of ``npm init`` and link to more and more things in ``node_modules/``. Since each bundle is self-contained, there will be a lot of duplication between bundles. For example, the webpack bootstrapping JS will be in every one of your bundles--even if you don't specifically import to any extra modules. At some point, and usually sooner than later, you should probably make a vendor bundle.

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

3. Reference your vendor bundle in ``base.htm`` *before* the ``links()`` call.

.. code-block:: html+mako

    <script src="/django_mako_plus/dmp-common.js"></script>
    <script src="${STATIC_URL}homepage/scripts/__bundle__.vendor.js"></script>
    ${ django_mako_plus.links(self) }


How do I create a single, sitewide bundle?
-----------------------------------------------

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

5. Specify the bundle as the JS link for all pages:

.. code-block:: python

    'CONTENT_PROVIDERS': [
        { 'provider': 'django_mako_plus.JsContextProvider' },
        { 'provider': 'django_mako_plus.WebpackJsLinkProvider',
          'filepath': 'homepage/scripts/__bundle__.js',
          'duplicates': False,
        },
    ],

The above settings hard code the bundle location for all apps. Since 'duplicates' is False, the bundle will be included once per request, even if your base template (the ``links()`` call) is run multiple times by subtemplates.


How do I create multi-app bundles?
-------------------------------------

Somewhere in between a sitewide bundle and app-specific bundles lives the multi-app bundle.  Suppose you want app1 and app2 in one bundle and app3, app4, and app5 in another.  The following commands create the two needed entry files:

::

    python3 manage.py dmp_webpack --overwrite --single homepage/scripts/__entry_1__.js app1 app2
    python3 manage.py dmp_webpack --overwrite --single homepage/scripts/__entry_2__.js app3 app4 app5

Then follow the same logic as the previous question (sitewide bundle) to include them in webpack's config and in the provider run.
