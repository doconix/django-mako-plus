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
        ${ django_mako_plus.providers(self, 'styles') }
    </head>

When enabled, DMP looks for ``app_folder/styles/index.scss``.  If it exists, DMP checks the timestamp of the compiled version, ``app_folder/styles/index.css``, to see if if recompilation is needed.  If needed, it runs ``scss`` before generating ``<link type="text/css" />`` for the file. 

During development, this check is done every time the template is rendered.  During production, this check is done only once -- the first time the template is rendered. 

Rendering Other Pages
------------------------------

But suppose you need to autorender the JS or CSS from a page *other than the one currently rendering*?  For example, you need to include the CSS and JS for ``otherpage.html`` while ``mypage.html`` is rendering.  This is a bit of a special case, but it has been useful at times.

To include CSS and JS by name, use the following within any template on your site (``mypage.html`` in this example):

::

    ## instead of using the normal:
    ## ${ django_mako_plus.providers(self, 'styles') }
    ##
    ## specify the app and page name:
    ${ django_mako_plus.template_providers(request, 'homepage', 'otherpage.html', context, 'styles')

    ...

    ## instead of using the normal:
    ## ${ django_mako_plus.providers(self, 'scripts') }
    ##
    ## specify the app and page name:
    ${ django_mako_plus.template_providers(request, 'homepage', 'otherpage.html', context, 'scripts')

Rendering Nonexistent Pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This special case is for times when you need the CSS and JS autorendered, but don't need a template for HTML.  The ``force`` parameter allows you to force the rendering of CSS and JS files, even if DMP can't find the HTML file.   Since ``force`` defaults True, the calls just above will render even if the template isn't found.  

In other words, this behavior already happens; just use the calls above.  Even if ``otherpage.html`` doesn't exist, you'll get ``otherpage.css`` and ``otherpage.js`` in the current page content.

Under the Hood: Providers
-------------------------------

The static files system is built to be extended for custom file types.  When you call ``providers()`` within a template, DMP iterates through a list of providers (``django_mako_plus.BaseProvider`` subclasses).  You can customize the behavior of these providers in your ``settings.py`` file.  Here's a very basic version:

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                ...
                'STATIC_FILE_PROVIDERS': [
                    # generates links for app/styles/template.css
                    { 'provider': 'django_mako_plus.CssLinkProvider' },
                    
                    # generates links for app/scripts/template.js
                    { 'provider': 'django_mako_plus.JsLinkProvider' },
                    
                    # adds marked context variables to the JS namespace
                    { 'provider': 'django_mako_plus.JsContextProvider' },
                    
                    # compiles app/styles/template.scss to app/styles/template/css
                    { 'provider': 'django_mako_plus.CompileScssProvider' },
                    
                    # compiles app/styles/template.less to app/styles/template/css
                    { 'provider': 'django_mako_plus.CompileLessProvider' },
                ],
            }
        }
    ]
    
Each type of provider takes additional settings that allow you to customize locations, automatic compilation, etc.  The following more-detailed version enumerates all the options (set to their defaults).  

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                ...
                'STATIC_FILE_PROVIDERS': [
                    # generates links for app/styles/template.css
                    { 
                        'provider': 'django_mako_plus.CssLinkProvider' 
                        'group': 'styles',
                        'weight': 0,
                        'filename': '{appdir}/styles/{template}.css',
                    },
                    
                    # generates links for app/scripts/template.js
                    { 
                        'provider': 'django_mako_plus.JsLinkProvider' 
                        'group': 'scripts',
                        'weight': 0,
                        'filename': '{appdir}/scripts/{template}.js',
                    },
                    
                    # adds marked context variables to the JS namespace
                    { 
                        'provider': 'django_mako_plus.JsContextProvider' 
                        'group': 'scripts',
                        'weight': 5,
                    },
                    
                    # compiles app/styles/template.scss to app/styles/template/css
                    { 
                        'provider': 'django_mako_plus.CompileScssProvider' 
                        'group': 'styles',
                        'weight': 10,  
                        'source': '{appdir}/styles/{template}.scss',
                        'compiled': '{appdir}/styles/{template}.css',
                        'command': [ shutil.which('scss'), '--unix-newlines', '{appdir}/styles/{template}.scss', '{appdir}/styles/{template}.css' ],
                    },
                    
                    # compiles app/styles/template.less to app/styles/template/css
                    { 
                        'provider': 'django_mako_plus.CompileLessProvider' 
                        'group': 'styles',
                        'weight': 10,  
                        'source': '{appdir}/styles/{template}.less',
                        'compiled': '{appdir}/styles/{template}.css',
                        'command': [ shutil.which('lessc'), '--source-map', '{appdir}/styles/{template}.less', '{appdir}/styles/{template}.css' ],
                    },
                ],
            }
        }
    ]
    
Custom Providers
^^^^^^^^^^^^^^^^^^^^^^^^^^

Creating new provider classes is easy.  The following is an example of a custom provider class.  Once you create the class, simply reference it in your settings.py file.

.. code:: python

    from django_mako_plus import BaseProvider
    from django_mako_plus.utils import merge_dicts

    class YourCustomproviders(BaseProvider):
        default_options = merge_dicts(BaseProvider.default_options, {  
            'any': 'additional',
            'options': 'should',
            'be': 'specified',
            'here': '.',
        })
        
        def init(self):
            # This is called from the constructor.
            # It runs once per template (at production).
            # Place any setup code here, or omit the
            # method if you don't need it.
            # 
            # Variables set by DMP:
            #    self.app_dir = '/absolute/path/to/app/'
            #    self.template_name = 'current template name without extension'
            #    self.options = { 'dictionary': 'of all options' }
            #    self.cgi_id = 'a unique number - see the docs'
            
        def get_content(self, request, context):
            # This is called during template rendering
            # It runs once per template - each time providers()
            # is called.
            #
            # This method sbould return the content to be added
            # to the rendered output.
            # 
            return '<div>Some content or css or js or whatever</div>'
            
            