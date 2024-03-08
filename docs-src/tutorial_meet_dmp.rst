.. _tutorial_meet_dmp:

T1: Meet DMP
==========================

.. contents::
    :depth: 2

I'll assume you've just installed Django-Mako-Plus according to the `installation instructions <installation.html>`_. You should have a ``mysite`` project directory that contains a ``homepage`` app. I'll further assume you know how to open a terminal/console and ``cd`` to the ``mysite`` directory. Most of the commands below are typed into the terminal in this directory.

**Quick Start:** You already have a default page in the new app, so fire up your server with ``python3 manage.py runserver`` and go to http://localhost:8000/homepage/index/.

You should see a congratulations page. If you don't, go back to the installation section and walk through the steps again. Your console might have valuable error messages to help troubleshoot things.

For the Impatient
-----------------------

If you are an experienced web developer and just want to get going, check out the example files in your new app:

* ``homepage/template/base.htm``
* ``homepage/template/index.htm``
* ``homepage/styles/index.css``
* ``homepage/scripts/index.js``

These files contain example code that follows the primary patterns of DMP.


Your New App
----------------------

Let's explore the directory structure of your new app:

::

    homepage/
        media/
        scripts/
            index.js
        styles/
            base.css
            index.css
        templates/
            base_ajax.htm
            base.htm
            index.html
        views/
            __init__.py
        __init__.py
        apps.py
        models.py
        tests.py

The directories should be fairly self-explanatory. Note they are **different** than a traditional Django app structure.  In short, put images and other support files in media/, Javascript in scripts/, CSS in styles/, html files in templates/, and Django views in views/.

    Note that a common pattern among Django developers is converting several files to directories: ``models.py`` to ``models/`` and ``tests.py`` to ``tests/``, but that's a discussion outside of DMP.


Your First Pages
------------------

Let's start with the two primary html template files: ``base.htm`` and ``index.html``.

``index.html`` is pretty simple:

.. code-block:: html+mako

    <%inherit file="base.htm" />

    <%block name="content">
        <div class="content">
          <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
          <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
          <h4 class="utc-time">Current time in UTC: ${ utc_time }</h4>
        </div>
    </%block>

If you are familiar with Django templates, you'll recognize the template inheritance in the ``<%inherit/>`` tag. However, this is Mako code, not Django code, so the syntax is a little different. The file defines a single block, called ``content``, that is plugged into the block by the same name in the code below.

The real HTML is kept in the ``base.htm`` file. It looks like this:

.. code-block:: html+mako

    ## this is the skeleton of all pages on in this app - it defines the basic html tags
    <!DOCTYPE html>
    <html>
        <meta charset="UTF-8">
        <head>

            <title>homepage</title>

            ## add any site-wide scripts or CSS here; for example, jquery:
            <script src="http://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

            ## render the static file links with the same name as this template
            <script src="/django_mako_plus/dmp-common.min.js"></script>
            ${ django_mako_plus.links(self) }

        </head>
        <body>

            <header>
                <h1>Welcome to the homepage app!<h1>
            </header>

            <main>
                <%block name="content">
                    Site content goes here in sub-templates.
                </%block>
            </main>

        </body>
    </html>


Pay special attention to the ``<%block name="content">`` section, which is overridden in ``index.html``. The page given to the browser will look exactly like ``base.htm``, but the ``content`` block will come from ``index.html`` rather than the one defined in the supertemplate.

The purpose of the inheritance from ``base.htm`` is to get a consistent look, menu, etc. across all pages of your site. When you create additional pages, simply override the ``content`` block, similar to the way ``index.html`` does it.

Possible Errors
-----------------------

First, don't erase anything in the base.htm file. In particular, ``django_mako_plus.links(self)`` and the ``dmp-common.min.js`` script are important. As much as you probably want to clean up the mess, try your best to leave these alone.

**'Undefined' object has no attribute 'get\_static'**

If you get this error, you might need to update a setting in ``settings.py``. Ensure that DMP is imported in the ``DEFAULT_TEMPLATE_IMPORTS`` list:

.. code-block:: python

    'DEFAULT_TEMPLATE_IMPORTS': [
        'import django_mako_plus',
    ]

Then clear out the compiled templates caches:

::

    python3 manage.py dmp_cleanup

**DMP_CONTEXT is not defined**

If you get this error, the ``/django_mako_plus/dmp-common.min.js`` script is not being loaded.  Check the following:

* Is the ``<script>`` tag for this file in your ``base.htm``?  If there, did it get moved below the ``links(self)`` call?  This script must be loaded on every page of your site (i.e. in the base template), and it must be loaded before DMP calls are made.
* Is the url pattern for this file working?  Check your ``urls.py`` file for ``include('django_mako_plus.urls')``.  The DMP ``urls.py`` file contains a direct pattern for this file that allows Django to find it.


Goodbye, urls.py
-----------------------

In the installation procedures above, you set your urls.py file to look something like the following:

.. code-block:: python

    from django.urls import include, path, re_path
    from django.contrib import admin

    urlpatterns = [
        # the built-in Django administrator
        re_path(r'^admin/', admin.site.urls),

        # urls for any third-party apps go here

        # the DMP router - this should normally be the last URL listed
        path('', include('django_mako_plus.urls')),
    ]

Rather than listing every. single. page. on. your. site. in the ``urls.py`` file, the router figures out the destination via a convention. The first url part is taken as the app to go to, and the second url part is taken as the view to call. See the advanced topics if you want to customize this behavior.

For example, the url ``/homepage/index/`` routes as follows:

-  The first url part ``homepage`` specifies the app that will be used.
-  The second url part ``index`` specifies the view or html page within the app. In our example:
-  The router first looks for ``homepage/views/index.py``. In this case, it fails because we haven't created it yet.
-  It then looks for ``homepage/templates/index.html``. It finds the file, so it renders the html through the Mako templating engine and returns it to the browser.

The above illustrates the easiest way to show pages: simply place .html files in your templates/ directory. This is useful for pages that don't have any "work" to do. Examples might be the "About Us" and "Terms of Service" pages. There's usually no functionality or permissions issues with these pages, so no view function is required.

You might be wondering about default URLs, such as ``http://www.yourserver.com/``.  When the url doesn't contain the app and the page, DMP uses the default app and page specified in your settings. Search for ``DEFAULT_APP`` and ``DEFAULT_PAGE`` in the full `settings documentation </basics_settings.html>`_ for more information.
