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

Detailed Options
--------------------------------

Specify the source paths and link format by overriding default options in settings. DMP merges ``CONTENT_PROVIDERS`` in your settings file wuth its defaults, so you can override a single option or many options. The following is the full set of options for these providers:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    {   'provider': 'django_mako_plus.JsContextProvider',
                        'group': 'styles',
                        'enabled': True,
                        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
                    },
                    {   'provider': 'django_mako_plus.CssLinkProvider',
                        'group': 'styles',
                        'enabled': True,
                        'filepath': None,
                        'link': None,
                        'link_attrs': {},
                        'skip_duplicates': True,
                    },
                    {   'provider': 'django_mako_plus.JsLinkProvider',
                        'group': 'styles',
                        'enabled': True,
                        'filepath': None,
                        'link': None,
                        'link_attrs': {},
                        'skip_duplicates': False,
                    },
                ],
            },
        },
    ]

Primary options:

:filepath:
    Specifies the search path DMP uses to find the static file for a given template.  The possible values are:

    * If ``None``, the providers call a built-in method that returns the pattern you saw in the tutorial: ``<app>/styles/<template>.css`` and ``<app>/styles/<template>.js``.
    * If a *function or lambda*, the function is called: ``func(provider)``. The ``provider`` object contains useful information, such as template name, extension, app name and config object, various paths, and options. Specifying a lambda is the typical way to customize the filepath. See the examples below for more on this.
    * If a *string*, it is used directly. This is useful when you want to hard code a file path.

    See the examples below for specifying custom file paths.

:link:
    Generates the link to be inserted into the rendering template. The possible values are:

    * If ``None``, the providers call a built-in method that generates the links: ``<link rel="stylesheet" .../>`` and ``<script src="..." ...></script>``.
    * If a *function or lambda*, the function is called: ``func(provider)``. The ``provider`` object contains useful information, such as template name, extension, app name and config object, various paths, and options. Specifying a lambda is the typical way to customize the link. See the examples below for more on this.
    * If a *string*, it is used directly. This is useful when you want to hard code a link.

    See the examples below for specifying custom link elements.

:link_attrs:
    Specifies additional attributes for the link tag, such as ``async``, ``type``, ``rel``, etc.

:skip_duplicates:
    Specifies how DMP should act when duplicate links are created by two providers (or two runs of the same provider). In the case of CSS files, the second link is unnecessary. In the case of JS files, a second link usually means the script should run a second time.

Less used options:

:group:
    Allows you to separate the printing of links into two or more groups. For example, if you need half the providers to run at the top of your template and half at the bottom, you could specify two groups: "top" and "bottom". To run only the top links, include this: ``${ django_mako_plus.links(self, group="top") }``.

:enabled:
    Specifies whether a provider is enabled or disabled (skipped). For example, if you specify ``'enabled': DEBUG``, a provider will run during development but be skipped at production.


Example: Custom Paths
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

The provider options in ``settings.py`` look like this:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    {   'provider': 'django_mako_plus.JsContextProvider' },
                    {   'provider': 'django_mako_plus.CssLinkProvider',
                        'filepath': lambda p: os.path.join('static', p.app_config.name, 'css', p.template_relpath + '.css'),
                    },
                    {   'provider': 'django_mako_plus.JsLinkProvider',
                        'filepath': lambda p: os.path.join('static', p.app_config.name, 'js', p.template_relpath + '.js'),
                    },
                ],
            },
        },
    ]

Also, since DMP looks for templates in the app directory, be sure to write the render call to the new structure:

.. code-block:: python

    @view_function
    def process_request(request):
        ...
        return request.dmp.render('homepage/index.html', ...)


By specifying the filepath with a lambda function, we can use the following attributes of the provider objects:

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


Example: Custom Links
-------------------------------------

Suppose we need a dynamic onLoad event to run with each template-related CSS file. In short, we want to generate custom CSS link elements.

    If the event were the same across all CSS link elements, we could simply override the ``link_attrs`` value in the options. But for a truly unique tag for each template, we'll need to generate the full link.

The provider options in ``settings.py`` look like this:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    {   'provider': 'django_mako_plus.JsContextProvider' },
                    {   'provider': 'django_mako_plus.CssLinkProvider',
                        'filepath': lambda p: os.path.join(p.app_config.name, 'styles', p.template_relpath + '.css'),
                        'link': lambda p: """<link rel="stylesheet" onLoad="custFunc('{app}/{tmpl}')" data-context="{uid}" href="{path}?{vid}" />""".format(
                            app=p.app_config.name,
                            tmpl=p.template_name,
                            uid=p.provider_run.uid,
                            path=os.path.join(STATIC_URL, p.filepath).replace(os.path.sep, '/'),
                            vid=p.version_id,
                        ),
                    },
                    {   'provider': 'django_mako_plus.JsLinkProvider' },
                ],
            },
        },
    ]

Not the following in the above link.

* The ``data-context`` attribute is set to the context (provider run) uid. Be sure to include this in any custom links so the client-side DMP script can find the element.
* The ``p.version_id`` variable is used as a cache buster. This id is calculated from the file "last modified" time and a hash of the file contents. When you change the file, the changed version_id will force client browsers to download the new file.

By specifying the link with a lambda function, we can use the following attributes of the provider objects:

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
* ``p.version_id`` - the unique id calculated from the file modified time and contents

*Hints:*

1. Be sure DMP's logging is set to "DEBUG" level (in settings). Then check the server logs; DMP's providers print a lot of useful information to help you troubleshoot. The file paths printed should be especially useful.
2. If the command is failing, you can copy the exact command being run from your server logs. Try running this command manually at a new terminal.
3. Open the browser source (not the parsed DOM in the console, but the actual content being sent from the server). Inspect the link elements and paths for problems.
