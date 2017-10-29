Rendering CSS and JS
================================

In the `tutorial <tutorial_css_js.html>`_, you learned how to automatically include CSS and JS based on your page name .  
If your page is named ``mypage.html``, DMP will automatically include ``mypage.css`` and ``mypage.js`` in the page content.  Skip back to the `tutorial <tutorial_css_js.html>`_ if you need a refresher.

Preprocessors like Scss and Less
-----------------------------------

If you are using preprocessors for your CSS or JS, DMP can automatically compile files.  While this could alternatively be done with an editor plugin or with a 'watcher' process, letting DMP compile for you keeps the responsibility within your project settings (rather than per-programmer-dependent setups).

Suppose your template ``index.html`` contains the typical code:

.. code:: html

    <head>
        ${ django_mako_plus.get_static(self, 'styles') }
    </head>

When enabled, DMP looks for ``app_folder/styles/index.scss``.  If it exists, DMP checks the timestamp of the compiled version, ``app_folder/styles/index.css``, to see if if recompilation is needed.  If needed, it runs ``scss`` before generating ``<link type="text/css" />`` for the file. 

During development, this check is done every time the template is rendered.  During production, this check is done only once -- the first time the template is rendered. 

Rendering Other Pages
------------------------------

But suppose you need to autorender the JS or CSS from a page *other than the one currently rendering*?  For example, you need to include the CSS and JS for ``otherpage.html`` while ``mypage.html`` is rendering.  This is a bit of a special case, but it has been useful at times.

To include CSS and JS by name, use the following within any template on your site (``mypage.html`` in this example):

::

    ## instead of using the normal:
    ## ${ django_mako_plus.get_static(self, 'styles') }
    ##
    ## specify the app and page name:
    ${ django_mako_plus.get_template_static(request, 'homepage', 'otherpage.html', context, 'styles')

    ...

    ## instead of using the normal:
    ## ${ django_mako_plus.get_static(self, 'scripts') }
    ##
    ## specify the app and page name:
    ${ django_mako_plus.get_template_static(request, 'homepage', 'otherpage.html', context, 'scripts')

Rendering Nonexistent Pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This special case is for times when you need the CSS and JS autorendered, but don't need a template for HTML.  The ``force`` parameter allows you to force the rendering of CSS and JS files, even if DMP can't find the HTML file.   Since ``force`` defaults True, the calls just above will render even if the template isn't found.  

In other words, this behavior already happens; just use the calls above.  Even if ``otherpage.html`` doesn't exist, you'll get ``otherpage.css`` and ``otherpage.js`` in the current page content.

Skipping Duplicates
-------------------------------

In rare cases, static file links ``<link ...>`` can show on a page more than once.  For example, this can happen when you ``<%include />`` a subtemplate within a ``for`` loop.  If that subtemplate contains a ``get_static()`` call, you'll get the same CSS links on each run of the loop.

Generally, the best way to handle this is to refactor your code so the duplicate calls don't occur.  However, if this isn't the right solution in a given situation, you can ask DMP to automatically skip duplicate includes by adding the ``duplicates`` parameter:

::

    ${ django_mako_plus.get_template_static(self, 'styles', duplicates=False) }

With the above call, DMP will include only one reference to each filename within a given request.

Providers
--------------------

When you call ``get_static()`` within a template, DMP iterates through a list of providers (``django_mako_plus.static_files.BaseProvider`` subclasses).  You can customize the behavior of these providers in your ``settings.py`` file:

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                ...
                'STATIC_FILE_PROVIDERS': {
                    # creates <link> when styles/template.css exists
                    'django_mako_plus.static_files.CssProvider': {},
                    
                    # creates <script> when scripts/template.js exists
                    'django_mako_plus.static_files.JsProvider': {},
                    
                    # *.scss compiling
                    # specify the `command` as a list (see Python's subprocess module)
                    # Special format keywords for use in the options:
                    #     {appdir} - The app directory for the template being rendered (full path).
                    #     {template} - The name of the template being rendered, without its extension.
                    'django_mako_plus.static_files.CompileProvider': {
                        'source': '{appdir}/styles/{template}.scss',
                        'compiled': '{appdir}/styles/{template}.css',
                        'command': [ shutil.which('scss'), '--unix-newlines', '{appdir}/styles/{template}.scss', '{appdir}/styles/{template}.css' ],
                    },

                    # *.less compiling
                    'django_mako_plus.static_files.CompileProvider': {
                        'source': '{appdir}/styles/{template}.less',
                        'compiled': '{appdir}/styles/{template}.css',
                        'command': [ shutil.which('lessc'), '--source-map', '{appdir}/styles/{template}.less', '{appdir}/styles/{template}.css' ],
                    },

                    # *.py (Transcript) compiling
                    'django_mako_plus.static_files.CompileProvider': {
                        'source': '{appdir}/scripts/{template}.py',
                        'compiled': '{appdir}/scripts/__javascript__/{template}.js',
                        'command': [ '/usr/bin/env, 'python3' '-m transcrypt '-m -b', '{appdir}/scripts/{template}.py', '{appdir}/scripts/__javascript__/{template}.js' ],
                    },
                },                
            }
        }
    ]
    
The first two providers, ``CssProvider`` and ``JsProvider``, generate the automatic links in your template.  Again, these are triggered by the call to ``django_mako_plus.get_static(self, 'group')``, where group is either "styles" or "scripts". 

The third provider compiles ``*.scss`` files. The options are specified with two special keywords sent to string .format(): ``{appdir}`` and ``{template}``.  The ``{appdir}`` keyword is the app folder for the current template (given as a full, absolute path).  The ``{template}`` keyword is the name of current template (without its extension).  Using these special keywords, three options are constructed so DMP knows the source file path, the compiled file path, and the executable command.  When the source file is newer than the compiled file, DMP runs the command.

The fourth provider compiles ``*.less`` files. 

The fifth provider compiles Transcrypt ``*.py`` files to Javascript.  