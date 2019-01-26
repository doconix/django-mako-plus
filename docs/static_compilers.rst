Sass, Less, & More
======================================

    Precompilers can be also be triggered by editor plugins and watcher processes. Use whatever method works best for your workflow.

DMP can automate compilation of your Sass and Less files--plus many others, from Stylus to Coffeescript to Typescript to Transcrypt.

When ``links(self)`` is called by your template, these providers compare your source file timestamps against their output files. If an update is needed, the appropriate compiler is run.

    During development, this check is done every time the template is rendered.  During production, this check is done the first time the template is rendered. If you update your files, you need to bounce the server (we assume you've done compiling beforehand anyway).



First, be sure you've installed `Sass <https://sass-lang.com/>`_ or `Less <http://lesscss.org/>`_ and that you can run them from the command line.


Detailed Options
--------------------------------

Specify the comiler comand, source location, and target location in settings. DMP merges ``CONTENT_PROVIDERS`` in your settings file wuth its defaults, so you can override a single option or many options. The following is the full set of options for these providers:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    # this should always be listed first
                    { 'provider': 'django_mako_plus.JsContextProvider' },

                    # Sass precompiler provider
                    { 'provider': 'django_mako_plus.CompileScssProvider',
                      'group': 'styles',
                      'enabled': True,
                      'sourcepath': None,
                      'targetpath': None,
                      'command': [],
                    },

                    # Less precompiler provider
                    { 'provider': 'django_mako_plus.CompileLessProvider',
                      'group': 'styles',
                      'enabled': True,
                      'sourcepath': None,
                      'targetpath': None,
                      'command': [],
                    },

                    # Generic provider for any language
                    { 'provider': 'django_mako_plus.CompileProvider',
                      'group': 'styles',
                      'enabled': True,
                      'sourcepath': None,
                      'targetpath': None,
                      'command': [],
                    },

                    # link providers should be listed AFTER compile providers
                    # see DMP docs /static_links.html for these provider options
                    { 'provider': 'django_mako_plus.CssLinkProvider' },
                    { 'provider': 'django_mako_plus.JsLinkProvider' },
                ],
            },
        },
    ]

Primary options:

:sourcepath:
    Specifies the search path DMP uses to find the source file (.scss, .less, etc.). The possible values are:

    * If ``None``, the providers call a built-in method that returns ``<app>/styles/<template>.scss`` or ``<app>/styles/<template>.less``.
    * If a *function or lambda*, the function is called: ``func(provider)``. The ``provider`` object contains useful information, such as template name, extension, app name and config object, various paths, and options. Specifying a lambda is the typical way to customize the filepath. See the examples below for more on this.
    * If a *string*, it is used directly. This is useful when you want to hard code a file path.

:targetpath:
    Specifies the output path for the generated file. The possible values are:

    * If ``None``, the providers call a built-in method that returns ``<app>/styles/<template>.css``.
    * If a *function or lambda*, the function is called: ``func(provider)``. The ``provider`` object contains useful information, such as template name, extension, app name and config object, various paths, and options. Specifying a lambda is the typical way to customize the filepath. See the examples below for more on this.
    * If a *string*, it is used directly. This is useful when you want to hard code a file path.

:command:
    A list to be sent to Python's ``subprocess`` module to run the external precompiler. If "falsey" (None, empty list), the provider calls a built-in method. For example, the default Sass command uses the following list:

    ::

        [ shutil.which('sass'),
          '--source-map',
          '--load-path={}'.format(settings.BASE_DIR),
          self.sourcepath,
          self.targetpath,
        ]

Less used options:

:group:
    Allows you to separate the printing of links into two or more groups. For example, if you need half the providers to run at the top of your template and half at the bottom, you could specify two groups: "top" and "bottom". To run only the top links, include this: ``${ django_mako_plus.links(self, group="top") }``.

:enabled:
    Specifies whether a provider is enabled or disabled (skipped). For example, if you specify ``'enabled': DEBUG``, a provider will run during development but be skipped at production.


Example: Sass Files
-------------------------------------

Suppose we want to modify the output name of the Sass compile provider. Instead of generating filenames with ``<template>.css``, we want output names to be ``<template>.scss.css``. We'll locate the ``.scss`` source files and the ``.scss.css`` generated files in the ``styles/`` directory (the DMP convention).

    What's the reason behind this example? The ``.scss.css`` extension makes it easy differentiate between generated CSS files and which are regular non-generated CSS files. This is just one way among many to differentiate.

In the following setup, note the changes to 1) the Sass compile provider's output name, and 2) the CSS link provider's search filepath.

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    {   'provider': 'django_mako_plus.JsContextProvider' },
                    {   'provider': 'django_mako_plus.CompileScssProvider',
                        'sourcepath': lambda p: os.path.join(BASE_DIR, p.app_config.name, 'styles', p.template_relpath + '.scss'),
                        'targetpath': lambda p: os.path.join(BASE_DIR, p.app_config.name, 'styles', p.template_relpath + '.scss.css'),
                    },
                    {   'provider': 'django_mako_plus.CssLinkProvider',
                        'filepath': lambda p: os.path.join(BASE_DIR, p.app_config.name, 'styles', p.template_relpath + '.scss.css'),
                    },
                    {   'provider': 'django_mako_plus.JsLinkProvider' },
                ],
            },
        },
    ]

By specifying the paths with lambda functions, we can use the following attributes of the provider objects:

* ``p.template_name`` - the name of the template, without extension
* ``p.template_relpath`` - the path of the template, relative to the ``app/templates`` directory. This is usually the same as ``template_name``, but it can be different if in a subdir of templates (e.g. ``homepage/templates/forms/login.html`` -> ``forms/login``.
* ``p.template_ext`` - the extension of the template filename
* ``p.app_config`` - the AppConfig the template resides in
* ``p.app_config.name`` - the name of the app
* ``p.template`` - the Mako template object
* ``p.template.filename`` - full path to template file
* ``p.options`` - the options for this provider (defaults + settings.py)
* ``p.provider_run.uid`` - the unique context id (needed when creating links)
* ``p.provider_run.request`` - the request object

*Hints:*

1. Be sure DMP's logging is set to "DEBUG" level (in settings). Then check the server logs; DMP's providers print a lot of useful information to help you troubleshoot. The file paths printed should be especially useful.
2. If the command is failing, you can copy the exact command being run from your server logs. Try running this command manually at a new terminal.
3. Open the browser source (not the parsed DOM in the console, but the actual content being sent from the server). Inspect the link elements and paths for problems.


Example: Less files in dist/
-----------------------------------------

Suppose we want to compile Less files to the ``dist/`` folder under our project root. The following are examples of the file paths we want:

* ``homepage/styles/index.scss`` compiles to ``dist/css/homepage.index.css``
* ``account/styles/login.scss`` compiles to ``dist/css/account.login.css``

In the following setup, note the changes to 1) the Sass compile provider's output name, and 2) the CSS link provider's search filepath.

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    {   'provider': 'django_mako_plus.JsContextProvider' },
                    {   'provider': 'django_mako_plus.CompileLessProvider',
                        'sourcepath': lambda p: os.path.join(BASE_DIR, p.app_config.name, 'styles', p.template_relpath + '.less'),
                        'targetpath': lambda p: os.path.join(BASE_DIR, 'dist', f'{p.app_config.name}.{p.template_relpath}.css'),
                    },
                    {   'provider': 'django_mako_plus.CssLinkProvider',
                        'filepath': lambda p: os.path.join(BASE_DIR, 'dist', f'{p.app_config.name}.{p.template_relpath}.css'),
                    },
                    {   'provider': 'django_mako_plus.JsLinkProvider' },
                ],
            },
        },
    ]

By specifying the paths with lambda functions, we can use the following attributes of the provider objects:

* ``p.template_name`` - the name of the template, without extension
* ``p.template_relpath`` - the path of the template, relative to the ``app/templates`` directory. This is usually the same as ``template_name``, but it can be different if in a subdir of templates (e.g. ``homepage/templates/forms/login.html`` -> ``forms/login``.
* ``p.template_ext`` - the extension of the template filename
* ``p.app_config`` - the AppConfig the template resides in
* ``p.app_config.name`` - the name of the app
* ``p.template`` - the Mako template object
* ``p.template.filename`` - full path to template file
* ``p.options`` - the options for this provider (defaults + settings.py)
* ``p.provider_run.uid`` - the unique context id (needed when creating links)
* ``p.provider_run.request`` - the request object


*Hints:*

1. Be sure DMP's logging is set to "DEBUG" level (in settings). Then check the server logs; DMP's providers print a lot of useful information to help you troubleshoot. The file paths printed should be especially useful.
2. If the command is failing, you can copy the exact command being run from your server logs. Try running this command manually at a new terminal.
3. Open the browser source (not the parsed DOM in the console, but the actual content being sent from the server). Inspect the link elements and paths for problems.


Example: Transcrypt
--------------------------

`Transcrypt <https://www.transcrypt.org/>`_ is a library that transpiles Python code into Javascript. It lets us write browser scripts in our favorite language rather than that *other* one...

Modern web development practices would usually transpile using a bundler like ``webpack``. But there may be situations when you want DMP to trigger compilation, and DMP's generic compile provider makes it easy.

The following settings automatically transcrypt ``<app>/scripts/*.py`` files.

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    # regular providers: context, JS, and CSS files
                    {   'provider': 'django_mako_plus.JsContextProvider' },
                    {   'provider': 'django_mako_plus.JsLinkProvider' },
                    {   'provider': 'django_mako_plus.CssLinkProvider' },

                    # transcrypt app/scripts/*.py files: compiler + linker
                    {   'provider': 'django_mako_plus.CompileProvider',
                        'sourcepath': lambda p: os.path.join(p.app_config.name, 'scripts', p.template_relpath + '.py'),
                        'targetpath': lambda p: os.path.join(p.app_config.name, 'scripts', '__target__', p.template_relpath + '.js'),
                        'command': lambda p: [
                            shutil.which('transcrypt'),
                            '--map',
                            '--build',
                            '--nomin',
                            os.path.join(BASE_DIR, p.app_config.name, 'scripts', p.template_relpath + '.py'),
                        ],
                    },
                    {   'provider': 'django_mako_plus.JsLinkProvider',
                        'filepath': lambda p: os.path.join(p.app_config.name, 'scripts', '__target__', p.template_relpath + '.js'),
                        'link_attrs': {
                            'type': 'module',
                            'async': 'true',
                        },
                    },
                ]
            },
        }
    ]

A few notes about these options:

* Regular CSS and Javascript files are still included (first three providers).
* ``targetpath`` contains the reference to ``./__target__`` because Transcrypt always outputs to that directory.
* ``shutil.which`` is similar to running ``/usr/bin/env`` on Unix. It searches the system path for the given program.
* The final ``JsLinkProvider`` adds the module attribute because Transcrypt outputs JS *modules*, and browsers require ``type="module"`` for module scripts.
