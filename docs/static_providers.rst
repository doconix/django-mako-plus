Under the Hood: Providers
================================


The framework is built to be extended for custom file types.  When you call ``links()`` within a template, DMP iterates through a list of providers (``django_mako_plus.BaseProvider`` subclasses).  You can customize the behavior of these providers in your ``settings.py`` file.  Here's a very basic version:

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    # adds JS context - should be listed first
                    { 'provider': 'django_mako_plus.JsContextProvider' },

                    # compiles app/styles/template.scss to app/styles/template.css
                    { 'provider': 'django_mako_plus.CompileScssProvider' },

                    # compiles app/styles/template.less to app/styles/template/css
                    { 'provider': 'django_mako_plus.CompileLessProvider' },

                    # generates links for app/styles/template.css
                    { 'provider': 'django_mako_plus.CssLinkProvider' },

                    # generates links for app/scripts/template.js
                    { 'provider': 'django_mako_plus.JsLinkProvider' },
                ],
            }
        }
    ]

Each type of provider takes additional settings that allow you to customize locations, automatic compilation, etc.  When reading most options, DMP runs the option through str.format() with the following formatting kwargs:

* {appname} - The app name for the template being rendered.
* {template} - The name of the template being rendered, without its extension.
* {appdir} - The app directory for the template being rendered (full path).
* {staticdir} - The static directory as defined in settings.

    **Order Matters:**  Just like Django middleware, the providers are run in order.  If one provider depends on the work of another, be sure to list them in the right order.  For example, the ``JsContextProvider`` provides context variables for scripts, so it must be placed before ``JsLinkProvider``.  That way, the variables are loaded when the scripts run.

The following more-detailed version enumerates all the options (set to their defaults).

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    # adds JS context - should be listed first
                    {
                        'provider': 'django_mako_plus.JsContextProvider'
                        'group': 'scripts',
                        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
                    },

                    # compiles app/styles/template.scss to app/styles/template.css
                    {
                        'provider': 'django_mako_plus.CompileScssProvider'
                        'group': 'styles',
                        'source': '{appdir}/styles/{template}.scss',
                        'output': '{appdir}/styles/{template}.css',
                        'command': [ shutil.which('scss'), '--unix-newlines', '{appdir}/styles/{template}.scss', '{appdir}/styles/{template}.css' ],
                    },

                    # compiles app/styles/template.less to app/styles/template/css
                    {
                        'provider': 'django_mako_plus.CompileLessProvider'
                        'group': 'styles',
                        'source': '{appdir}/styles/{template}.less',
                        'output': '{appdir}/styles/{template}.css',
                        'command': [ shutil.which('lessc'), '--source-map', '{appdir}/styles/{template}.less', '{appdir}/styles/{template}.css' ],
                    },

                    # generates links for app/styles/template.css
                    {
                        'provider': 'django_mako_plus.CssLinkProvider'
                        'group': 'styles',
                        'filename': '{appdir}/styles/{template}.css',
                        'skip_duplicates': True,
                    },

                    # generates links for app/scripts/template.js
                    {
                        'provider': 'django_mako_plus.JsLinkProvider'
                        'group': 'scripts',
                        'filename': '{appdir}/scripts/{template}.js',
                        'async': False,
                    },
                ],
            }
        }
    ]

As an example, consider the `Transcrypt files <https://www.transcrypt.org/>`_ project, which transpiles Python code into Javascript. It lets you write browser scripts in our favorite language (note the source looks for ``.py`` files. The provider settings tells DMP to compile your Transcrypt files when needed. The first provider transpiles the source, and the second one creates the ``<script>`` link to the output file.

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    {
                        'provider': 'django_mako_plus.CompileProvider',
                        'group': 'scripts',
                        'source': '{appdir}/scripts/{template}.py',
                        'output': '{appdir}/scripts/__javascript__/{template}.js',
                        'command': [ 'transcrypt', '--map', '--build', '--nomin', '{appdir}/scripts/{template}.py' ],
                    },
                    {
                        'provider': 'django_mako_plus.JsLinkProvider',
                        'group': 'scripts',
                        'filename': '{appdir}/scripts/__javascript__/{template}.js',
                    },
                ],
            }
        }
    ]


Custom Providers
-------------------------------


Suppose you need custom preprocessing of static files or custom template content.  Your future may include creating a new provider class. Fortunately, these are pretty simple classes. Once you create the class, simply reference it in your settings.py file.

.. code:: python

    from django_mako_plus import BaseProvider
    from django_mako_plus.utils import merge_dicts

    class YourCustomProvider(BaseProvider):
        default_options = merge_dicts(BaseProvider.default_options, {
            'any': 'additional',
            'options': 'should',
            'be': 'specified',
            'here': '.',
        })

    def start(self, provider_run, data):
        '''
        Called on the *main* template's provider list as the run starts.
        Initialize values in the data dictionary here.
        '''
        pass

    def provide(self, provider_run, data):
        '''Called on *each* template's provider list in the chain - use provider_run.write() for content'''
        pass

    def finish(self, provider_run, data):
        '''
        Called on the *main* template's provider list as the run finishes
        Finalize values in the data dictionary here.
        '''
        pass

