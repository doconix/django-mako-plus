Webpack Example
================================

If you're using a transpiled laguage, such as Coffee or TypeScript, you probably have webpack already up and running.  This example should help explain the specifics for integrating it with DMP scripts.

For demonstration purposes, let's assume you have ``*.js``, ``*.coffee`` and ``*.ts`` in the same project.  All of these need to go into the ``__entry__.js`` file.

The directory structure for the ``account`` app might look like the following:

::

    project/
        account/
            scripts/
                base.js
                base.ts
                index.coffee
                index.js
                index.ts
                another.js
            styles/
                base.css
            templates/
                base.htm
                index.html


Since they share a name, ``index.coffee``, ``index.js``, and ``index.ts`` need to execute with ``index.html``.


Installation
--------------------

The following should already be done (see the webpack docs if not).

* ``npm init``
* ``npm install webpack coffeescript coffee-loader typescript ts-loader``
* Create the ``package.json`` file as described above.
* Create the ``webpack.config.js`` file as described above.


Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The typical DMP entry file contains Javascript and CSS files.  We need to tell DMP's ``manage.py dmp webpack`` command to find ``*.coffee`` and ``*.ts`` files as well as ``*.js``.

This is done in ``settings.py`` under the DMP options:

.. code:: python

    'WEBPACK_PROVIDERS': [
        { 'provider': 'django_mako_plus.CssLinkProvider' },
        { 'provider': 'django_mako_plus.JsLinkProvider' },
        {
            'provider': 'django_mako_plus.JsLinkProvider',
            'filepath': os.path.join('scripts', '{template}.coffee'),
        },
        {
            'provider': 'django_mako_plus.JsLinkProvider',
            'filepath': os.path.join('scripts', '{template}.ts'),
        },
    ],

    Remember that Webpack is going to do the transpiling (not DMP).  The purpose of ``manage.py dmp webpack`` is to connect the files together so webpack knows where to put them in the bundle.


Create your entry file(s):

::

    python3 manage.py dmp_webpack account --overwrite

The above command creates ``account/scripts/__entry__.js``.

::

    (context => {
        DMP_CONTEXT.appBundles["account/index"] = () => {
            require("../styles/base.css");
            require("./base.js");
            require("./base.ts");
            require("./index.js");
            require("./index.coffee");
            require("./index.ts");
        };
    })(DMP_CONTEXT.get());


The entry file requires all files connected to ``index.html`` and its supertemplate ``base.htm``.  The four providers run in the order they appear in settings.

    1. The command starts with ``base.htm``.  It runs our four providers (in order) and finds three files: CSS, JS, and Typescript.
    2. The command goes to ``index.html``.  It runs our four providers (in order) and finds three files: JS, Coffee, and Typescript.

When webpack builds the bundle, it will include all seven files in the function keyed to ``account/index`` (we'll run this function when the page loads).


Create the Bundle
~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure your ``webpack.config.js`` file has loaders for Coffee and Typescript (this will just a simplified example):

::

    const path = require('path');
    const MiniCssExtractPlugin = require("mini-css-extract-plugin");

    module.exports = {
        devtool: 'source-map',
        entry: {
            'account': './account/scripts/__entry__.js',
        },
        output: {
            path: path.resolve(__dirname),
            filename: '[name]/scripts/__bundle__.js'
        },
        plugins: [
            new MiniCssExtractPlugin({
                path: path.resolve(__dirname),
                filename: '[name]/styles/__bundle__.css'
            })
        ],
        module: {
            rules: [
                {
                    test: /\.coffee$/,
                    use: [ 'coffee-loader' ],
                },
                {
                    test: /\.ts$/,
                    use: [ 'ts-loader' ],
                },
                {
                    test: /\.css$/,
                    use: [
                        MiniCssExtractPlugin.loader,
                        'css-loader',
                    ]
                }
            ]
        }
    };

Now create the bundle:

::

    npm run build

Webpack should create ``account/scripts/__bundle__.js`` and ``account/styles/__bundle__.css``.


Link the Bundle
~~~~~~~~~~~~~~~~~~~~~

The bundles are linked the same as described on the `webpack page </static_webpack.html>`_:

.. code:: python

    # providers - these provide the <link> and <script> tags that the webpack providers make
    'CONTENT_PROVIDERS': [
        { 'provider': 'django_mako_plus.JsContextProvider' },           # adds the JS context
        { 'provider': 'django_mako_plus.WebpackCssLinkProvider' },      # <link> tags for CSS bundle
        { 'provider': 'django_mako_plus.WebpackJsLinkProvider' },       # <script> tags for JS bundle(s)
        { 'provider': 'django_mako_plus.WebpackJsCallProvider' },       # call the bundle function for the current page
    ],
