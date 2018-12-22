Including Static Files
================================

In the `tutorial <tutorial_css_js.html>`_, you learned how to automatically include CSS and JS based on your page name .
If your page is named ``mypage.html``, DMP will automatically include ``mypage.css`` and ``mypage.js`` in the page content.  Skip back to the `tutorial <tutorial_css_js.html>`_ if you need a refresher.

Open ``base.htm`` and look at the following code:

::

    ## render the static file links for this template
    ${ django_mako_plus.links(self) }

The calls to ``links()`` include the ``<link>`` and ``<script>`` tags for the template name and all of its supertemplates. These links are placed at the end of your ``<head>`` section.  (Just a few years ago, common practice was to place script tags at the end of the body, but modern browsers with asyncronous and deferred scripts have put them back in the body.)

This all works because the ``index.html`` template extends from the ``base.htm`` template. If you fail to inherit from ``base.htm`` or ``base_ajax.htm``, DMP won't be able to include the support files.


Javascript Matters
----------------------------------

Your ``base.htm`` file contains the following script link:

::

    <script src="/django_mako_plus/dmp-common.min.js"></script>

This file contains a few functions that DMP uses to run scripts and send context variables to your javascript.  It is important that this link be loaded **before** any DMP calls are done in your templates.

When running in production mode, your web server (IIS, Nginx, etc.) should serve this file rather than Django.  Or you may want to include the file in a bundler like webpack.  In any case, the file just needs to be included on every page of your site, so do it in an efficient way for your setup.

The following is an example setting for Nginx:

::

    location /django_mako_plus/dmp-common.min.js {
        alias /to/django_mako_plus/scripts/dmp-common.min.js;
    }

If you don't know the location of DMP on your server, try this command:

::

    python3 -c 'import django_mako_plus; print(django_mako_plus.__file__)'


Preprocessors (Scss and Less)
-----------------------------------

If you are using preprocessors for your CSS or JS, DMP can automatically compile files.  While this could alternatively be done with an editor plugin or with a 'watcher' process, letting DMP compile for you keeps the responsibility within your project settings (rather than per-programmer-dependent setups).

When this feature is enabled, DMP looks for ``app_folder/styles/index.scss``.  If it exists, DMP checks the timestamp of the compiled version, ``app_folder/styles/index.css``, to see if if recompilation is needed.  If needed, it runs ``scss`` before generating ``<link type="text/css" />`` for the file.

During development, this check is done every time the template is rendered.  During production, this check is done only once -- the first time the template is rendered.

To enable automatic compiling, uncomment the appropriate provider to your settings.py.  The following setting adds Scss compiling to the normal JS Context, JS, and CSS providers:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'CONTENT_PROVIDERS': [
                    { 'provider': 'django_mako_plus.JsContextProvider' },     # adds JS context - this should normally be listed first
                    { 'provider': 'django_mako_plus.CompileScssProvider' },   # autocompiles Scss files
                    # { 'provider': 'django_mako_plus.CompileLessProvider' },   # autocompiles Less files
                    { 'provider': 'django_mako_plus.CssLinkProvider' },       # generates links for app/styles/template.css
                    { 'provider': 'django_mako_plus.JsLinkProvider' },        # generates links for app/scripts/template.js
                ],
            },
        },
    ]



Rendering Other Pages
------------------------------

But suppose you need to autorender the JS or CSS from a page *other than the one currently rendering*?  For example, you need to include the CSS and JS for ``otherpage.html`` while ``mypage.html`` is rendering.  This is a bit of a special case, but it has been useful at times.

To include CSS and JS by name, use the following within any template on your site (``mypage.html`` in this example):

.. code-block:: html+mako

    ## instead of using the normal:
    ## ${ django_mako_plus.links(self) }
    ##
    ## specify the app and page name:
    ${ django_mako_plus.template_links(request, 'homepage', 'otherpage.html', context)


Rendering Nonexistent Pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This special case is for times when you need the CSS and JS autorendered, but don't need a template for HTML.  The ``force`` parameter allows you to force the rendering of CSS and JS files, even if DMP can't find the HTML file.   Since ``force`` defaults True, the calls just above will render even if the template isn't found.

In other words, this behavior already happens; just use the calls above.  Even if ``otherpage.html`` doesn't exist, you'll get ``otherpage.css`` and ``otherpage.js`` in the current page content.
