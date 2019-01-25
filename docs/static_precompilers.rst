Compiling Sass and Less
================================

If you are using preprocessors for your CSS or JS, DMP can automatically compile files when you load pages.

    This can also be done with editor plugins or watcher processes (``webpack --watch``). Use whatever method is best for your setup.

First, be sure you've installed `Sass <https://sass-lang.com/>`_ or `Less <http://lesscss.org/>`_ and that you can run them from the command line.

When you render an HTML file (i.e. when ``links()`` is called on ``base.htm``), DMP looks for ``<app>/styles/<template>.scss``.  DMP checks the timestamp of the compiled version, ``<app>/styles/<template>.scss``, to see if if recompilation is needed.  If needed, it runs ``scss`` or ``lessc`` before generating links for hte file.

During development, this check is done every time the template is rendered.  During production, this check is done the first time the template is rendered. If you update your files, you need to bounce the server (we assume you've done compiling beforehand anyway).

Precompilers are specified in your settings file. For example, the following adds `Sass <https://sass-lang.com/>`_ compilation (`Less <http://lesscss.org/>`_ is commented out):

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    { 'provider': 'django_mako_plus.JsContextProvider' },     # adds JS context - this should normally be listed first
                    { 'provider': 'django_mako_plus.CompileScssProvider' },   # autocompiles Scss files
                    # { 'provider': 'django_mako_plus.CompileLessProvider' }, # autocompiles Less files
                    { 'provider': 'django_mako_plus.CssLinkProvider' },       # generates links for app/styles/template.css
                    { 'provider': 'django_mako_plus.JsLinkProvider' },        # generates links for app/scripts/template.js
                ],
            },
        },
    ]
