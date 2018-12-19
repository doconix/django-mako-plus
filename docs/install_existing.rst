Existing Project
=========================

If you already have an existing project that you'd like to integrate DMP into, follow the directions in this section.

Ensure you have Python 3.4+ installed (``python3 --version``).  If you are using virtual environments, be sure to activate that first.


Install Django, Mako, and DMP
-----------------------------------

DMP works with Django 1.9+, including the 2.0 releases.

The following will install all three dependencies:

::

    pip3 install --upgrade django-mako-plus

(note that on Windows machines, ``pip3`` may need to be replaced with ``pip``)

If you need to add DMP to an existing Django project, you have two options:

1. **Convert your project to the DMP structure.** This switches your
   project over to the layout of a DMP-style project.
2. **Keep your existing Django-style structure** with minimal changes.

This section describes Option 1, which gives you the full benefit of the automatic DMP routing and midleware. If you just need to render templates using the Mako language (e.g. Option 2), jump to `Rending Templates the Standard Way: ``render()`` <#rending-templates-the-standard-way-render>`__.

Edit Your ``settings.py`` File:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add ``django_mako_plus`` to the end of your ``INSTALLED_APPS`` list:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'django_mako_plus',
    ]

Add ``django_mako_plus.RequestInitMiddleware`` to your ``MIDDLEWARE``
list:

.. code-block:: python

    MIDDLEWARE = [
        ...
        'django_mako_plus.RequestInitMiddleware',
        ...
    ]

Add a logger to help you debug (optional but highly recommended!):

.. code-block:: python

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
standard Django project already has the ``TEMPLATES =`` line and the 'django' template backend.  You probably just need to add the ``django_mako_plus`` dictionary below.

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                # see the DMP documentation, "configuration options" page for available options
            },
        },
        {
            'NAME': 'django',
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            ...
        },
    ]

Add the following to serve your static files. Note that a standard Django project already has the first ``STATIC_URL =`` line.

.. code-block:: python

    STATIC_URL = '/static/'   # you probably already have this
    STATICFILES_DIRS = (
        # SECURITY WARNING: this next line must be commented out at deployment
        BASE_DIR,
    )
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

Clean out all the cached template files. This should be done **anytime you make a DMP change in settings.py**:

::

    python3 manage.py dmp_cleanup

Enable the Django-Mako-Plus Router
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add the Django-Mako-Plus router in your ``urls.py`` file (the default admin is also included here for completeness).

.. code-block:: python

    from django.conf.urls import url, include

    urlpatterns = [
        url('', include('django_mako_plus.urls')),
    ]



Create a DMP-Style App
-----------------------------------

Change to your project directory in the terminal/console, then create a new Django-Mako-Plus app with the following:

.. code-block:: python

    python3 manage.py dmp_startapp homepage

**After** the new ``homepage`` app is created, add your new app to the ``INSTALLED_APPS`` list in ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'homepage',
    ]

Congratulations. You're ready to go!


Load it Up!
-----------------------------------

Start your web server with the following:

.. code-block:: python

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
