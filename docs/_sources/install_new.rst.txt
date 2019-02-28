.. _install_new:

New Project
======================

All of the commands in both Django and DMP are run at the command line. On Linux/Mac, this is usually a bash terminal. On Windows, this is the command prompt (cmd), PowerShell (powershell), or Git Bash.

Open a terminal, and check that Python 3.4 or later is active:

.. tabs::

   .. group-tab:: Linux/Mac

        .. code:: bash

            python3 --version

   .. group-tab:: Windows

        .. code:: powershell

            python --version

If an older Python (such as 2.7) is reported, you likely need to do one of the following:

1. Install a `newer version of Python <https://www.python.org/downloads/>`_
2. Activate a `different virtual environment <https://docs.python.org/3/tutorial/venv.html>`_.


Install Django, Mako, and DMP
----------------------------------

DMP works with Django 1.9+, although most testing today happens on Django 2.x.

Install Django, Mako, and DMP with the following:

.. tabs::

   .. group-tab:: Linux/Mac

        .. code:: bash

            pip3 install --upgrade django-mako-plus

   .. group-tab:: Windows

        .. code:: powershell

            pip install --upgrade django-mako-plus



Create a Django project
----------------------------------

Create a Django project, and specify that you want a DMP-style project layout:

.. tabs::

   .. group-tab:: Linux/Mac

        .. code:: bash

            python3 -m django_mako_plus dmp_startproject mysite

   .. group-tab:: Windows

        .. code:: powershell

            python -m django_mako_plus dmp_startproject mysite

You can, of course, name your project anything you want, but in the sections below, I'll assume you called your project ``mysite``.

Then migrate to synchronize your database and create a superuser:

.. tabs::

   .. group-tab:: Linux/Mac

        .. code:: bash

            cd mysite
            python3 manage.py migrate
            python3 manage.py createsuperuser

   .. group-tab:: Windows

        .. code:: powershell

            cd mysite
            python manage.py migrate
            python manage.py createsuperuser


Create a DMP-Style App
----------------------------------

Create a new Django-Mako-Plus app with the following:

.. tabs::

   .. group-tab:: Linux/Mac

        .. code:: bash

            python3 manage.py dmp_startapp homepage

   .. group-tab:: Windows

        .. code:: powershell

            python manage.py dmp_startapp homepage

**After** the new ``homepage`` app is created, open ``mysite/settings.py`` in your favorite editor and add to the ``INSTALLED_APPS`` list:

.. code:: python

    INSTALLED_APPS = [
        ...
        'homepage',
    ]


Congratulations. You're ready to go!

Load it Up!
----------------------------------

Start your web server with the following:

.. tabs::

   .. group-tab:: Linux/Mac

        .. code:: bash

            python3 manage.py runserver

   .. group-tab:: Windows

        .. code:: powershell

            python manage.py runserver


If you get a message about unapplied migrations, ignore it for now and continue.

Open your web browser to http://localhost:8000/. You should see a message welcoming you to the homepage app.

Once everything is working, skip ahead to the :ref:`tutorial`.
