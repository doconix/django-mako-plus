Installation
==============================

This section shows how to install DMP with a new project as well as an existing project.

What kind of project do you have?

.. contents::
    :depth: 3


New Project
-----------------------------

Install Python and ensure you can run ``python3`` (or ``python``) at the command prompt. The framework requires Python 3.4+.

Install Django, Mako, and DMP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DMP works with Django 1.9+, including the 2.0 releases.

Install with the python installer:

::

    pip3 install django-mako-plus

Note that on Windows machines, ``pip3`` may need to be replaced with ``pip``:

::

    pip install django-mako-plus

Create a Django project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a Django project, and specify that you want a DMP-style project layout:

::

    python3 -m django_mako_plus dmp_startproject mysite

That might seem like a mouthful to type, but it's patterned after the standard Django method of creating projects.

You can, of course, name your project anything you want, but in the sections below, I'll assume you called your project ``mysite``.

Don't forget to migrate to synchronize your database and create a superuser:

::

    cd mysite
    python3 manage.py migrate
    python3 manage.py createsuperuser


Create a DMP-Style App
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change to your project directory in the terminal/console, then create a new Django-Mako-Plus app with the following:

.. code:: python

    python3 manage.py dmp_startapp homepage

**After** the new ``homepage`` app is created, add your new app to the ``INSTALLED_APPS`` list in ``settings.py``:

.. code:: python

    INSTALLED_APPS = [
        ...
        'homepage',
    ]

Congratulations. You're ready to go!

Load it Up!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Start your web server with the following:

.. code:: python

    python3 manage.py runserver

If you get a message about unapplied migrations, ignore it for now and continue.

Open your web browser to http://localhost:8000/. You should see a message welcoming you to the homepage app.

If everything is working, `skip ahead to the tutorial <tutorial.html>`_.






Existing Project
---------------------------------

If you already have an existing project that you'd like to integrate DMP into, follow the directions in this section.  First, install Python and ensure you can run ``python3`` (or ``python``) at the command prompt. The framework requires Python 3.4+.

Install Django, Mako, and DMP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DMP 3 works with Django 1.9+ and Mako 1.0+. It will support Django 2.0 when it is released.

Install with the python installer:

::

    pip3 install django-mako-plus

Note that on Windows machines, ``pip3`` may need to be replaced with ``pip``:

::

    pip install django-mako-plus


If you need to add DMP to an existing Django project, you have two options:

1. **Convert your project to the DMP structure.** This switches your
   project over to the layout of a DMP-style project.
2. **Keep your existing Django-style structure** with minimal changes.

This section describes Option 1, which gives you the full benefit of the automatic DMP router and midleware. If you need Option 2, jump to `Rending Templates the Standard Way: ``render()`` <#rending-templates-the-standard-way-render>`__.

Edit Your ``settings.py`` File:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add ``django_mako_plus`` to the end of your ``INSTALLED_APPS`` list:

.. code:: python

    INSTALLED_APPS = [
        ...
        'django_mako_plus',
    ]

Add ``django_mako_plus.RequestInitMiddleware`` to your ``MIDDLEWARE``
list:

.. code:: python

    MIDDLEWARE = [
        ...
        'django_mako_plus.RequestInitMiddleware',
        ...
    ]

Add a logger to help you debug (optional but highly recommended!):

.. code:: python

    DEBUG_PROPAGATE_EXCEPTIONS = DEBUG  # SECURITY WARNING: never set this True on a live site
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'dmp_simple': {
                'format': '%(levelname)s::DMP %(message)s'
            },
        },
        'handlers': {
            'dmp_console':{
                'level':'DEBUG',
                'class':'logging.StreamHandler',
                'formatter': 'dmp_simple'
            },
        },
        'loggers': {
            'django_mako_plus': {
                'handlers': ['dmp_console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }

Add the Django-Mako-Plus engine to the ``TEMPLATES`` list. Note that a
standard Django project already has the ``TEMPLATES =`` line and the 'django' template backend.

.. code:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                # see the options in the DMP docs if you want to customize anything
            },
        },
        {
            'NAME': 'django',
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            # ...
        },
    ]

Add the following to serve your static files. Note that a standard Django project already has the first ``STATIC_URL =`` line.

.. code:: python

    STATIC_URL = '/static/'   # you probably already have this
    STATICFILES_DIRS = (
        # SECURITY WARNING: this next line must be commented out at deployment
        BASE_DIR,
    )
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

Clean out all the cached template files. This should be done **anytime you make a DMP change in settings.py**:

::

    python manage.py dmp_cleanup

Enable the Django-Mako-Plus Router
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the Django-Mako-Plus router in your ``urls.py`` file (the default admin is also included here for completeness).

.. code:: python

    from django.conf.urls import url, include

    urlpatterns = [
        # urls for any third-party apps go here

        # adds all DMP-enabled apps
        url('', include('django_mako_plus.urls')),
    ]



Create a DMP-Style App
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change to your project directory in the terminal/console, then create a new Django-Mako-Plus app with the following:

.. code:: python

    python3 manage.py startapp --template=http://cdn.rawgit.com/doconix/django-mako-plus/master/app_template.zip --extension=py,htm,html homepage

**After** the new ``homepage`` app is created, add your new app to the
``INSTALLED_APPS`` list in ``settings.py``:

.. code:: python

    INSTALLED_APPS = [
        ...
        'homepage',
    ]

Congratulations. You're ready to go!

Load it Up!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Start your web server with the following:

.. code:: python

    python3 manage.py runserver

If you get a message about unapplied migrations, ignore it for now and
continue.

Open your web browser to http://localhost:8000/. You should see a
message welcoming you to the homepage app.

If everything is working, skip ahead to the tutorial.


Subdirectory: /mysite/
-----------------------------------

This section is for those that need Django is a subdirectory, such as ``/mysite``. If your Django installation is at the root of your domain, skip this section.

In other words, suppose your Django site isn't the only thing on your server. Instead of the normal url pattern, ``http://www.yourdomain.com/``, your Django installation is at ``http://www.yourdomain.com/mysite/``. All apps are contained within this ``mysite/`` directory.

This is accomplished in the normal Django way. Adjust your ``urls.py`` file to include the prefix:

::

    url('^mysite/', include('django_mako_plus.urls')),
