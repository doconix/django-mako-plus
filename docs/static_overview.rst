Overview
================================

    This page details how DMP supports traditional links. If you've moved on to bundling instead of direct links, these are not the droids you're looking for. Move along to the `bundling page </static_webpack.html>`_.

In the `tutorial <tutorial_css_js.html>`_, you learned how to automatically include CSS and JS based on your page name .
If your page is named ``mypage.html``, DMP will automatically include ``mypage.css`` and ``mypage.js`` in the page content.  Skip back to the `tutorial <tutorial_css_js.html>`_ if you need a refresher.

Here's what DMP can do for your static files:

:Automatic Links:
    Suppose ``index.html`` inherits from two supertemplates, and you have a ``.js`` file and a ``.css`` file for each:

    .. code-block:: sh

        base.htm        (base.js, base.css)
            |
        homepage.htm    (homepage.js, homepage.css)
            |
        index.html      (index.js, index.css)

    Why so many files for a single web page? It's a scoping issue. Since ``base.htm`` is the ancestor of **every** page on our site, its related JS and CSS link into every page. If a CSS style affects every page (such as the top menubar), it goes in ``base.css``. In like manner, the static files for ``homepage`` link into the pages of the homepage app. Put the code in the level for its scope.

    When ``index.html`` renders, DMP automatically creates the links for its support pages. That's all six files in this case!

:Inject Variables into Javascript:
    Custom variables are easy to send from view's ``process_request`` function to the rendering template scope (just put it in ``context`` when calling render). But getting values from ``process_request`` to the browser's Javascript scope is a bit more difficult. It requires encoding to JSON and html-based script tags. DMP makes it easy (just wrap the key with ``jscontext(...)`` when placing in the render context.

:Sass and Less Compiling:
    Just before DMP links the related CSS files into a page, it can run ``sass`` or ``lessc`` for you. I realize other options exist for this (editors, watchers), but personally, I prefer it because compilation happens via my project settings. If this benefits your workflow, it's here waiting...

:Webpack Bundling:
    Bundling vendor support files is pretty easy, but things get a little more difficult when page-specific code gets bundled. DMP allows appwide bundles, and it automatically runs the right bundle code for each page.



How It Works
-------------------

Open ``base.htm`` and look at the following code:

::

    ## render the static file links for this template
    ${ django_mako_plus.links(self) }

The call to ``links(self)`` triggers a number of "provider" classes to run. Each provider is responsible for adding specific types of links. For example, the ``JsContextProvider`` adds context variables to the rendered page; the ``CssLinkProvider`` adds ``<link rel="stylesheet"...>`` links for CSS files related to the current page (and its ancestors).

Since this call to ``links(self)`` exists in ``base.htm`` (and since all site pages extend from base), these providers trigger on every page of your site. Just be sure your pages extend from this supertemplate.

    DMP's default app (homepage) contains two "base" files: ``base.htm`` and ``base_ajax.htm``.  The first is for full pages (you know, the ones that start with ``<html>`` :).  The second is for page snippets like those created in ajax requests. Pretty much the only thing in ``base_ajax.htm`` is the call to links and a block for subpages to override.

``dmp-common.js``
----------------------------------

Lets go back to ``base.htm``.  Just above the call to ``links(self)`` you'll see the following:

::

    <script src="/django_mako_plus/dmp-common.min.js"></script>

DMP uses this script to make everything work on the browser side. For example, this script injects values sent from your view.py into the client-side JS scope. It's a small script (3K), and it's written in old-school Javascript (for a wide browser audience).

When running in production mode, your web server (IIS, Nginx, etc.) should serve this file (rather than Django).  Or it could be bundled with other vendor code. In any case, the file just needs to be included on every page of your site.

The following is an example setting for Nginx:

::

    location /django_mako_plus/dmp-common.min.js {
        alias /to/django_mako_plus/scripts/dmp-common.min.js;
    }

If you don't know the location of DMP on your server, try this command:

::

    python3 -c 'import django_mako_plus; print(django_mako_plus.__file__)'
