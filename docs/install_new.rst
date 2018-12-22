New Project
======================

Ensure you have Python 3.4+ installed (``python3 --version``), and check that you can run ``python3`` (or ``python``) at the command prompt.

If you are using virtual environments, be sure to activate that first.

Install Django, Mako, and DMP
----------------------------------

DMP works with Django 1.9+, including the 2.0 releases.

The following will install all three dependencies:

::

    pip3 install --upgrade django-mako-plus

(note that on Windows machines, ``pip3`` may need to be replaced with ``pip``)

Create a Django project
----------------------------------

Create a Django project, and specify that you want a DMP-style project layout:

::

    python3 -m django_mako_plus dmp_startproject mysite

You can, of course, name your project anything you want, but in the sections below, I'll assume you called your project ``mysite``.

Don't forget to migrate to synchronize your database and create a superuser:

::

    cd mysite
    python3 manage.py migrate
    python3 manage.py createsuperuser


Create a DMP-Style App
----------------------------------

Change to your project directory in the terminal/console, then create a new Django-Mako-Plus app with the following:

::

    python3 manage.py dmp_startapp homepage

**After** the new ``homepage`` app is created, add your new app to the ``INSTALLED_APPS`` list in ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'homepage',
    ]

Congratulations. You're ready to go!

Load it Up!
----------------------------------

Start your web server with the following:

::

    python3 manage.py runserver

If you get a message about unapplied migrations, ignore it for now and continue.

Open your web browser to http://localhost:8000/. You should see a message welcoming you to the homepage app.

If everything is working, `skip ahead to the tutorial <tutorial.html>`_.
