Rendering CSS and JS
================================

In the `tutorial <tutorial_css_js.html>`_, you learned how to automatically include CSS and JS based on your page name .  
If your page is named ``mypage.html``, DMP will automatically include ``mypage.css`` and ``mypage.js`` in the page content.  Skip back to the `tutorial <tutorial_css_js.html>`_ if you need a refresher.

Preprocessors (Scss and Less)
-----------------------------------

If you are using preprocessors for your CSS or JS, DMP can automatically compile files.  While this could alternatively be done with an editor plugin or with a 'watcher' process, letting DMP compile for you keeps the responsibility within your project settings (rather than per-programmer-dependent setups).

Suppose your template ``index.html`` contains the typical code:

.. code:: html

    <head>
        ${ django_mako_plus.links(self) }
    </head>

When enabled, DMP looks for ``app_folder/styles/index.scss``.  If it exists, DMP checks the timestamp of the compiled version, ``app_folder/styles/index.css``, to see if if recompilation is needed.  If needed, it runs ``scss`` before generating ``<link type="text/css" />`` for the file. 

During development, this check is done every time the template is rendered.  During production, this check is done only once -- the first time the template is rendered. 

Rendering Other Pages
------------------------------

But suppose you need to autorender the JS or CSS from a page *other than the one currently rendering*?  For example, you need to include the CSS and JS for ``otherpage.html`` while ``mypage.html`` is rendering.  This is a bit of a special case, but it has been useful at times.

To include CSS and JS by name, use the following within any template on your site (``mypage.html`` in this example):

::

    ## instead of using the normal:
    ## ${ django_mako_plus.links(self) }
    ##
    ## specify the app and page name:
    ${ django_mako_plus.template_links(request, 'homepage', 'otherpage.html', context)


Rendering Nonexistent Pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This special case is for times when you need the CSS and JS autorendered, but don't need a template for HTML.  The ``force`` parameter allows you to force the rendering of CSS and JS files, even if DMP can't find the HTML file.   Since ``force`` defaults True, the calls just above will render even if the template isn't found.  

In other words, this behavior already happens; just use the calls above.  Even if ``otherpage.html`` doesn't exist, you'll get ``otherpage.css`` and ``otherpage.js`` in the current page content.

Connecting Python and Javascript
-----------------------------------------------

In the `tutorial <tutorial_css_js.html>`_, you learned to send context variables to included *.js files using ``jscontext``:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function, jscontext
    from datetime import datetime

    @view_function
    def process_request(request):
        context = {
            jscontext('now'): datetime.now(),
        }
        return request.dmp_render('index.html', context)

DMP responds with a small script tag that adds the following to the ``<head>`` section.  

::

    <script type="text/javascript" src="/static/homepage/scripts/index.js?1509480811" data-context="{&#34;now&#34;: &#34;2017-10-31T20:13:33.084&#34;}"></script>
    
If you are paying close attention, you may have noticed that DMP actually sends a script snippet that, when run by the browser, creates the above tag with code.  Sending a script to add a script might seem as real as James Moriarty leaving the holodeck, but stick with me.  DMP does this because some frameworks (JQuery!) strip the ``<script>`` tags from ajax responses and trigger them manually.  Since the scripts run after the content is inserted into the DOM, the ``document.currentScript`` variable is null and unable to give the ``jscontext`` variables to your JS.  By running a script which inserts a script tag, the real script runs inline with the ``appendChild`` call, and ``document.currentScript`` gets magically set by the browser.  

tl;dr: Inserting the script tag with code skips past any ajax framework behavior, allowing your JS to get the ``jscontext`` variables from the script tags.
    
Reading the Attribute
^^^^^^^^^^^^^^^^^^^^^^^^
    
The task of getting the data from the script attribute to your Javascript namespace is fraught with danger.   While there are possible ways to do this, the suggested Master Sword is the following:

::

    (function(context) {
        // your code here, such as
        console.log(context);
    })(JSON.parse(document.currentScript.getAttribute('data-context')));

The drawback to this method is it only works with modern browsers.  The above code creates a closure for the ``context`` variable, which allows each of your scripts to use the same variable name without stepping on one another.  Clean namespaces.  Yummy.

If your users have older browsers, including any version of IE, this method can still work with `a polyfill <https://www.google.com/search?q=polyfill+currentscript>`_.

If you are using an onload callback function, such as a JQuery ready function, be sure to embed the callback within the closure.  The ``document.currentScript`` attribute only exists during the initial run of the script, so it's gone by the time the callback executes.  Here's an example:

::

    (function(context) {
        $(function() {
            // your code here, such as
            console.log(context);
        });
    })(JSON.parse(document.currentScript.getAttribute('data-context')));
    
Selecting on src=
~~~~~~~~~~~~~~~~~~~~~

The ``querySelector`` function is available on semi-modern browsers (including IE 9+):

::

    (function(context) {
        // your code here, such as
        console.log(context);
    })(JSON.parse(document.querySelector('script[src*="/homepage/scripts/index.js"]').getAttribute('data-context')));

The primary drawback of this approach is the hard-coded name selection can be fragile, such as when you change the template name and forget to match the code.


Other Approaches
^^^^^^^^^^^^^^^^^^^^

You've probably noticed that I haven't included the most direct approach: ``document.getElementById``, but I've skipped this approach because the ``<script>`` tag doesn't have an id.  If DMP set an id on the element, the Javascript would need to somehow get that id.  it just pushes the data transfer one level out, but we end up with the same problem.  The whole point of DMP is convention, with as little hard coding and configuration as possible.  For now, this method is ix-nayed.

Another method is encoding the data in the script src query string.  However, reading this from Javascript means we need a reference to the script tag, so once again we just pushed the problem one level out.

Finally, many examples online use the last item in ``document.scripts`` or the last script in the DOM.  This approach probably isn't the ticket because additional ``<script>`` elements are usually added to the DOM before the current one is running. This method worked well with browsers circa 2010, but not as well with today's browsers.


Groups
-----------------

Each provider class specifies a "group" it is part of. In the default providers, the two groups are ``scripts`` and ``styles``.  When you render the static file links in your template, providers from all groups are included:

::

    ${ django_mako_plus.links(self) }

However, if you need to split the link rendering into two or more places on a page, or if you only need style links for some reason, you can specify a group in the render:

::

    ${ django_mako_plus.links(self, group='styles') }

In the above call, only providers in the ``styles`` group are printed.

Groups are specified in the options for each provider, so you can change them to any string you need in the ``CONTENT_PROVIDERS`` section.

Under the Hood: Providers
-------------------------------

The framework is built to be extended for custom file types.  When you call ``links()`` within a template, DMP iterates through a list of providers (``django_mako_plus.BaseProvider`` subclasses).  You can customize the behavior of these providers in your ``settings.py`` file.  Here's a very basic version:

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    # generates links for app/styles/template.css
                    { 'provider': 'django_mako_plus.CssLinkProvider' },
                    
                    # generates links for app/scripts/template.js
                    { 'provider': 'django_mako_plus.JsLinkProvider' },
                    
                    # compiles app/styles/template.scss to app/styles/template/css
                    { 'provider': 'django_mako_plus.CompileScssProvider' },
                    
                    # compiles app/styles/template.less to app/styles/template/css
                    { 'provider': 'django_mako_plus.CompileLessProvider' },
                ],
            }
        }
    ]
    
Each type of provider takes additional settings that allow you to customize locations, automatic compilation, etc.  When reading most options, DMP runs the option through str.format() with the following formatting kwargs:

* ``appname`` - the name of the template's app
* ``appdir`` - the absolute path to the app directory
* ``template`` - the name of the template being rendered

The following more-detailed version enumerates all the options (set to their defaults).

::

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
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
                        'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
                        'async': True,
                        'defer': False,
                    },
                    
                    # compiles app/styles/template.scss to app/styles/template/css
                    { 
                        'provider': 'django_mako_plus.CompileScssProvider' 
                        'group': 'styles',
                        'weight': 10,  
                        'source': '{appdir}/styles/{template}.scss',
                        'output': '{appdir}/styles/{template}.css',
                        'command': [ shutil.which('scss'), '--unix-newlines', '{appdir}/styles/{template}.scss', '{appdir}/styles/{template}.css' ],
                    },
                    
                    # compiles app/styles/template.less to app/styles/template/css
                    { 
                        'provider': 'django_mako_plus.CompileLessProvider' 
                        'group': 'styles',
                        'weight': 10,  
                        'source': '{appdir}/styles/{template}.less',
                        'output': '{appdir}/styles/{template}.css',
                        'command': [ shutil.which('lessc'), '--source-map', '{appdir}/styles/{template}.less', '{appdir}/styles/{template}.css' ],
                    },
                ],
            }
        }
    ]
    
For example, the following compiles `Transcrypt files <https://www.transcrypt.org/>`_.  The first provider transpiles the source, and the second one creates the ``<script>`` link to the output file.

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
^^^^^^^^^^^^^^^^^^^^^^^^^^

Creating new provider classes is easy.  The following is an example of a custom provider class.  Once you create the class, simply reference it in your settings.py file.

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
            #    self.version_id = 'a unique number - see the docs'
            
        def get_content(self, request, context):
            # This is called during template rendering
            # It runs once per template - each time links()
            # is called.
            #
            # This method sbould return the content to be added
            # to the rendered output.
            # 
            return '<div>Some content or css or js or whatever</div>'
            
            