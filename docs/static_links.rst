CSS and JS
==========================

Out of the box, DMP is configured to serve regular JS and CSS files.  The default provider options are set as follows (you can override these in ``settings.py``:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    { 'provider': 'django_mako_plus.JsContextProvider' },  # adds JS context - this should normally be listed FIRST
                    { 'provider': 'django_mako_plus.CssLinkProvider' },    # generates links for app/styles/template.css
                    { 'provider': 'django_mako_plus.JsLinkProvider' },     # generates links for app/scripts/template.js
                ],
            },
        },
    ]

We described the first provider, ``JsContextProvider`` in the previous page. Providers are run in order, so be sure it's always the first one listed. It sets up the context and adds variables from your view function.

The other two providers, ``CssLinkProvider`` and ``JsLinkProvider`` generate ``<link>`` and ``<script>`` tags, respectively. As we discussed earlier, these not only create links for the current template (e.g. ``index.html``), but they also create links for supertemplates of the current page (e.g. ``base.htm``).

This mechanism provides several spots to put CSS and JS, depending on the scope you want affected. If the ``<footer>`` tag is in ``base.htm``, any CSS and/or JS related to it should probably be in ``base.css`` and ``base.js``.

Full Options
--------------------------------

You can change the source paths and link format by overriding default options in settings. DMP deep merges ``CONTENT_PROVIDERS`` in your settings file wuth its defaults, so you can override a single option or many options. The following is the full set of options for these providers:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    {
                        'provider': 'django_mako_plus.JsContextProvider',
                        'group': 'styles',
                        'enabled': True,
                        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
                    },{
                        'provider': 'django_mako_plus.CssLinkProvider',
                        'group': 'styles',
                        'enabled': True,
                        'filepath': None,
                        'link': None,
                        'skip_duplicates': True,
                    },{
                        'provider': 'django_mako_plus.JsLinkProvider',
                        'group': 'styles',
                        'enabled': True,
                        'filepath': None,
                        'link': None,
                        'skip_duplicates': False,
                        'async': False,
                    },
                ],
            },
        },
    ]

Primary options:

:filepath:
    Specifies the search path DMP uses to find the static file for a given template. Links are created only when filepaths exist. The possible values are:

    * If ``None``, the providers call a built-in method that returns the pattern you saw in the tutorial: ``<app>/styles/<template>.css`` and ``<app>/styles/<template>.js``.
    * If a *function or lambda*, the function is called: ``func(provider)``. The ``provider`` object contains useful information, such as template name, extension, app name and config object, various paths, and options. Specifying a lambda is the typical way to customize the filepath. See the examples below for more on this.
    * If a *string*, it is used directly. This is useful when you want to hard code a file path.

:link:
    Generates the link to be inserted into the rendering template. The possible values are:

    * If ``None``, the providers call a built-in method that generates the links: ``<link rel="stylesheet" .../>`` and ``<script src="..." ...></script>``.
    * If a *function or lambda*, the function is called: ``func(provider)``. The ``provider`` object contains useful information, such as template name, extension, app name and config object, various paths, and options. Specifying a lambda is the typical way to customize the link. See the examples below for more on this.
    * If a *string*, it is used directly. This is useful when you want to hard code a link.

:skip_duplicates:
    Specifies how DMP should act when duplicate links are created by two providers (or two runs of the same provider). In the case of CSS files, the second link is unnecessary. In the case of JS files, a second link usually means the script should run a second time.

:async:
    Specifies whether a script tag should be asynchronous: ``<script src="..." async="true"></script>``. Browsers normally run scripts synchronously, but modern sites often switch to asyncronous execution.

Less used options:

:group:
    Allows you to separate the printing of links into two or more groups. For example, if you need half the providers to run at the top of your template and half at the bottom, you could specify two groups: "top" and "bottom". To run only the top links, include this: ``${ django_mako_plus.links(self, group="top") }``.

:enabled:
    Specifies whether a provider is enabled or disabled (skipped). For example, if you specify ``'enabled': DEBUG``, a provider will run during development but be skipped at production.


Example: Specifying the Filepath
-------------------------------------

Suppose we want to use a traditional Django project structure (different from DMP convention):

::

    project/
        homepage/
            templates/
                homepage/
                    base.html
                    index.html
            models.py
            views.py
        static/
            css/
                homepage/
                    base.css
                    index.css
            js/
                homepage/
                    base.js
                    index.js

By specifying the filepath with a lambda function, we can use the following attributes of the provider objects:

    * ``provider.template_name`` - the name of the template, without extension
    * ``provider.template_relpath`` - the path of the template, relative to the ``app/templates`` directory. This is usually the same as ``template_name``, but it can be different if in a subdir of templates (e.g. ``homepage/templates/forms/login.html`` -> ``forms/login``.
    * ``provider.template_ext`` - the extension of the template filename
    * ``provider.app_config`` - the AppConfig the template resides in
    * ``provider.app_config.name`` - the name of the app
    * ``provider.template`` - the Mako template object
    * ``provider.template.filename`` - full path to template file
    * ``provider.options`` - the options for this provider (defaults + settings.py)


.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    {
                        'provider': 'django_mako_plus.JsContextProvider',
                    },{
                        'provider': 'django_mako_plus.CssLinkProvider',
                        'filepath': lambda:
                    },{
                        'provider': 'django_mako_plus.JsLinkProvider',
                        'filepath': None,
                    },
                ],
            },
        },
    ]
