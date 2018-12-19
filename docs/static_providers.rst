Under the Hood: Providers
================================


The framework is built to be extended for custom file types.  When you call ``links()`` within a template, DMP iterates through a list of providers (``django_mako_plus.BaseProvider`` subclasses).  You can customize the behavior of these providers in your ``settings.py`` file.

Here's a basic version:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    { 'provider': 'django_mako_plus.JsContextProvider' },     # adds JS context - this should normally be listed first
                    { 'provider': 'django_mako_plus.CompileScssProvider' },   # autocompiles Scss files
                    { 'provider': 'django_mako_plus.CompileLessProvider' },   # autocompiles Less files
                    { 'provider': 'django_mako_plus.CssLinkProvider' },       # generates links for app/styles/template.css
                    { 'provider': 'django_mako_plus.JsLinkProvider' },        # generates links for app/scripts/template.js
                ],

            }
        }
    ]


Setting Options
-------------------------------

Each provider has an options dictionary that allows you to adjust its behavior.  For example, link providers like ``JsLinkProvider`` allow custom search paths:

.. code-block:: python

    {
        'provider': 'django_mako_plus.JsContextProvider',
        'filepath': os.path.join('scripts', 'subdir', '{template}.js'),
    },


The following lists the complete options for all providers that come with DMP:

.. code-block:: python

    {
        # adds JS context - this should normally be listed first
        'provider': 'django_mako_plus.JsContextProvider',
        # whether enabled (see "Dev vs. Prod" in the DMP docs)
        'enabled': True,
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'scripts',
        # the encoder to use for the JSON structure
        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
    },
    {
        # autocompiles Scss files
        'provider': 'django_mako_plus.CompileScssProvider',
        # whether enabled (see "Dev vs. Prod" in the DMP docs)
        'enabled': True,
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'styles',
        # the source filename to search for
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}
        'sourcepath': os.path.join('styles', '{template}.scss'),
        # the destination filename to search for
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}, {sourcepath}
        'targetpath': os.path.join('styles', '{template}.css'),
        # the command to be run, as a list (see subprocess module)
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}, {sourcepath}, {targetpath}
        'command': [
            shutil.which('sass'),
            '--load-path=.',
            '{sourcepath}',
            '{targetpath}',
        ],
    },
    {
        # autocompiles Less files
        'provider': 'django_mako_plus.CompileLessProvider',
        'provider': 'django_mako_plus.CompileScssProvider',
        # whether enabled (see "Dev vs. Prod" in the DMP docs)
        'enabled': True,
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'styles',
        # the source filename to search for
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}
        'sourcepath': os.path.join('styles', '{template}.less'),
        # the destination filename to search for
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}, {sourcepath}
        'targetpath': os.path.join('styles', '{template}.css'),
        # the command to be run, as a list (see subprocess module)
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}, {sourcepath}, {targetpath}
        'command': [
            shutil.which('lessc'),
            '--source-map',
            '{sourcepath}',
            '{targetpath}',
        ],
    },
    {
        # generates links for app/styles/template.css
        'provider': 'django_mako_plus.CssLinkProvider',
        # whether enabled (see "Dev vs. Prod" in the DMP docs)
        'enabled': True,
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'styles',
        # the filename to search for (resolves to a single file, if it exists)
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}
        'filepath': os.path.join('styles', '{template}.css'),
        # if a template is rendered more than once in a request, we usually don't
        # need to include the css again.
        'skip_duplicates': True,
    },
    {
        # generates links for app/scripts/template.js
        'provider': 'django_mako_plus.JsLinkProvider',
        # whether this provider is enabled
        'enabled': True,
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'scripts',
        # the filename to search for (resolves to a single file, if it exists)
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}
        'filepath': os.path.join('scripts', '{template}.js'),
        # if a template is rendered more than once in a request, we should link each one
        # so the script runs again each time the template runs
        'skip_duplicates': False,
        # whether to create an async script tag
        'async': False,
    },
    {
        # generates links for app/styles/__bundle__.css (used with webpack)
        'provider': 'django_mako_plus.WebpackCssLinkProvider',
        # whether enabled (see "Dev vs. Prod" in the DMP docs)
        'enabled': True,
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'styles',
        # the filename to search for (resolves to a single file, if it exists)
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}
        'filepath': os.path.join('styles', '__bundle__.css'),
        # if a template is rendered more than once in a request, we usually don't
        # need to include the css again.
        'skip_duplicates': True,
    },
    {
        # generates links for app/scripts/__bundle__.js (used with webpack)
        'provider': 'django_mako_plus.WebpackJsLinkProvider',
        # whether enabled (see "Dev vs. Prod" in the DMP docs)
        'enabled': True,
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'scripts',
        # the filename to search for (resolves to a single file, if it exists)
        # if it does not start with a slash, it is relative to the app directory.
        # if it starts with a slash, it is an absolute path.
        # codes: {basedir}, {app}, {template}, {template_name}, {template_file}, {template_subdir}
        'filepath': os.path.join('scripts', '__bundle__.js'),
        # if a template is rendered more than once in a request, we should link each one
        # so the script runs again each time the template runs
        'skip_duplicates': False,
        # whether to create an async script tag
        'async': False,
    },
    {
        # activates the JS for the current template (used with webpack)
        'provider': 'django_mako_plus.WebpackJsCallProvider',
        # whether enabled (see "Dev vs. Prod" in the DMP docs)
        'enabled': True,
        # the group this provider is part of.  this only matters when
        # the html page limits the providers that will be called with
        # ${ django_mako_plus.links(group="...") }
        'group': 'scripts',
    },



Order Matters
--------------------

Just like Django middleware, the providers are run in order.  If one provider depends on the work of another, be sure to list them in the right order.  For example, the ``JsContextProvider`` provides context variables for scripts, so it must be placed before ``JsLinkProvider``.  That way, the variables are loaded when the scripts run.

    ``JsContextProvider`` should usually be listed first because several other providers depend on it.




Dev vs. Prod
-------------------------------

Providers are triggered by a call to ``${ django_mako_plus.links(self) }``.  By default, they run in both development and production mode.

The process might be a little different from dev to prod.  For example, certain providers may only be needed when ``DEBUG=True``.  Or in production mode, you may have options values that are slightly different.

Every provider has an ``enabled`` boolean option that sets whether it should be active or not.  Clever use of this variable can make providers activate under different circumstances.  The following setting uses ``settings.DEBUG`` to run the ``CompileScssProvider`` only during development:

::

    {
        'provider': 'django_mako_plus.CompileScssProvider',
        'enabled': DEBUG,  # this is in settings.py, so no need for the usual `settings.`
    }


Example: Sass Filenames
----------------------------------------

Sass normally compiles ``[name].scss`` to ``[name].css``.  The output file is placed in the same directory as the source file.  This can make it hard to differentiate the generated `*.css` files from normal non-sass css files.  It also makes it difficult to add a pattern for the generated files in ``.gitignore``.

Assuming you aren't bundling with something like webpack, there are at least two possibilities.

**Option 1: Place generated files in a top-level ``dist/`` folder in your project.**

.. code-block:: python

    {
        'provider': 'django_mako_plus.CompileScssProvider',
        'sourcepath': os.path.join('styles', '{template}.scss'),
        'targetpath': os.path.join('{basedir}', 'dist', '{app}', 'styles', '{template}.css'),
    },
    {
        'provider': 'django_mako_plus.CssLinkProvider',
        'filepath': os.path.join('{basedir}', 'dist', '{app}', 'styles', '{template}.css'),
    },

**Option 2: Use a custom extension for generated files, such as `[name].scss.css``.**

.. code-block:: python

    {
        'provider': 'django_mako_plus.CompileScssProvider',
        'sourcepath': os.path.join('styles', '{template}.scss'),
        'targetpath': os.path.join('styles', '{template}.scss.css'),
    },
    {
        'provider': 'django_mako_plus.CssLinkProvider',
        'filepath': os.path.join('styles', '{template}.scss.css'),
    },


Example: Running a Transpiler
-------------------------------

Transpiling is usually done with a bundler like ``webpack``.  However, there may be situations when you want DMP to trigger the transpiler.  Since the process is essentially the same as compiling Sass or Less, we just need to adjust the options to match our transpiler.

`Transcrypt <https://www.transcrypt.org/>`_ is a library that transpiles Python code into Javascript. It lets you write browser scripts in our favorite language rather than that other one.  The setup requires two providers:

1. A ``CompileProvider`` to run the transpiler when the source file changes.
2. A ``JsLinkProvider`` to link the generated javascript (transcrypt places the generated files in a subdirectory).

.. code-block:: python

    {
        'provider': 'django_mako_plus.CompileProvider',
        'group': 'scripts',
        'sourcepath': os.path.join('scripts', '{template_subdir}', '{template_name}.py'),
        'targetpath': os.path.join('scripts', '{template_subdir}', '__javascript__', '{template_name}.js'),
        'command': [
            shutil.which('transcrypt'),
            '--map',
            '--build',
            '--nomin',
            '{sourcepath}',
        ],
    },
    {
        'provider': 'django_mako_plus.JsLinkProvider',
        'filepath': os.path.join('scripts', '{template_subdir}', '__javascript__', '{template_name}.js'),
    },


Creating a Provider
------------------------

If you need something beyond the standard providers, you can `create a custom provider </static_custom.html>`_.
