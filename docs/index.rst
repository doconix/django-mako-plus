.. sidebar:: Show Me the Code:

    1. `Django Syntax vs. DMP Syntax <about.html#comparison-with-django>`_
    2. `Simple Template <tutorial_meet_dmp.html#your-new-app>`_
    3. `Basic View (.py file) <tutorial_views.html#t2-py-view-files>`_
    4. `Ajax Example <tutorial_ajax.html#a-simple-example>`_


Django-Mako-Plus
================================================

*Routing Django to Mako since 2013*

Code
-------------------------

https://github.com/doconix/django-mako-plus

Features
--------------------------

*DMP adds convention-over-configuration to Django:*

- `Uses standard Python </tutorial_meet_dmp.html>`_ in templates; no more weak-sauce Django templating.
- `Calls any view function </tutorial_views.html>`_ by convention instead of listing every. single. page. in urls.py.
- `Converts parameters </tutorial_urlparams.html>`_ in the URL and loads model objects by convention.
- Automatically `links .js and .css </tutorial_css_js.html>`_ in your HTML documents by convention.
- Automatically sets `context variables </tutorial_css_js.html#static-and-dynamic-javascript>`_ in the Javascript namespace.
- Provides `Django-style signals </topics_signals.html>`_.
- Extends Django's redirecting with `exception-based redirecting </topics_redirecting.html>`_.
- Supports `language translations </topics_translation.html>`_, `class-based views </topics_class_views.html>`_, and collection of `static files </topics_providers.html>`_.
- Includes a comprehensive `test suite <https://github.com/doconix/django-mako-plus/tree/master/tests>`_.

DMP doesn't replace Django; the standard router and template engine can be used alongside it.


Quick Start
----------------------

.. code:: bash

    # install django, mako, and DMP
    pip3 install django-mako-plus

    # create a new project with a 'homepage' app
    python3 -m django startproject --template=http://cdn.rawgit.com/doconix/django-mako-plus/master/project_template.zip mysite
    cd mysite
    python3 manage.py startapp --template=http://cdn.rawgit.com/doconix/django-mako-plus/master/app_template.zip --extension=py,htm,html homepage

    # open mysite/settings.py and append 'homepage' to the INSTALLED_APPS list
    INSTALLED_APPS = [
        ...
        'homepage',
    ]

    # run initial migrations and run the server
    python3 manage.py migrate
    python3 manage.py runserver

    # Open a browser to http://localhost:8000/

Note that on Windows, ``python3`` is ``python`` and ``pip3`` is ``pip``. Python 3+ is required.

Contents
------------

.. toctree::
    :maxdepth: 2

    about
    upgrade_notes
    installation
    tutorial
    topics



Compatability
----------------

DMP requires Python 3.4+ and Django 1.9+.

It will continue with Django 2.0 when released.

