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
        'filepath': lambda provider: os.path.join(provider.app_config.name, 'scripts', provider.template_name + '.js'),
    },

While the options for each provider are different, most allow either a string or a function/lambda (e.g. ``filepath`` above). This allows path names to be created as simple strings or using full logic and method calls. If a function is specified, it should take one parameter: the provider. Every provider contains the following:


* ``provider.template_name`` - the name of the template, without extension
* ``provider.template_relpath`` - the path of the template, relative to the ``app/templates`` directory. This is usually the same as ``template_name``, but it can be different if in a subdir of templates (e.g. ``homepage/templates/forms/login.html`` -> ``forms/login``.
* ``provider.template_ext`` - the extension of the template filename
* ``provider.app_config`` - the AppConfig the template resides in
* ``provider.app_config.name`` - the name of the app
* ``provider.template`` - the Mako template object
* ``provider.template.filename`` - full path to template file
* ``provider.options`` - the options for this provider (defaults + settings.py)

    When running in production mode, provider objects are created once and then cached, so any lambda functions are run at system startup (not every request).


Order Matters
--------------------

Just like Django middleware, the providers are run in order.  If one provider depends on the work of another, be sure to list them in the right order.  For example, the ``JsContextProvider`` provides context variables for scripts, so it must be placed before ``JsLinkProvider``.  That way, the variables are loaded when the scripts run.

    ``JsContextProvider`` should usually be listed first because several other providers depend on it.

Another example is the need to list ``ScssCompileProvider`` before ``CssLinkProvider``, which allows the first to create the .css file for the second to find.


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
        'sourcepath': lambda provider: os.path.join(provider.app_config.name, 'styles', provider.template_name + '.scss'),
        'targetpath': lambda provider: os.path.join('dist', provider.app_config.name, 'styles', provider.template_name + '.css'),
    },
    {
        'provider': 'django_mako_plus.CssLinkProvider',
        'filepath': lambda provider: os.path.join('dist', provider.app_config.name, 'styles', provider.template_name + '.css'),
    },

**Option 2: Use a custom extension for generated files, such as `[name].scss.css``.**

.. code-block:: python

    {
        'provider': 'django_mako_plus.CompileScssProvider',
        'sourcepath': lambda provider: os.path.join(provider.app_config.name, 'styles', provider.template_name + '.scss'),
        'targetpath': lambda provider: os.path.join('dist', provider.app_config.name, 'styles', provider.template_name + '.scss.css'),
    },
    {
        'provider': 'django_mako_plus.CssLinkProvider',
        'filepath': lambda provider: os.path.join('dist', provider.app_config.name, 'styles', provider.template_name + '.scss.css'),
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
        'sourcepath': lambda provider: os.path.join(provider.app_config.name, 'scripts', provider.template_name + '.py'),
        'targetpath': lambda provider: os.path.join(provider.app_config.name, 'scripts', '__javascript__', provider.template_name + '.js'),
        'command': lambda provider: [
            shutil.which('transcrypt'),
            '--map',
            '--build',
            '--nomin',
            os.path.join(provider.app_config.name, 'scripts', provider.template_name + '.py'),
        ],
    },
    {
        'provider': 'django_mako_plus.JsLinkProvider',
        'filepath': lambda provider: os.path.join(provider.app_config.name, 'scripts', '__javascript__', provider.template_name + '.js')
    },


Creating a Provider
------------------------

If you need something beyond the standard providers, you can `create a custom provider </static_custom.html>`_.
