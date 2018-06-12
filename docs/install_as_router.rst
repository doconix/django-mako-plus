Using DMP to Route by Convention
======================================

One of DMP's primary missions is to fix Django's need to have every. endpoint. in. your. system. listed. in. urls.py.  The following shows how to use DMP to route by convention -- essentially shrinking your ``urls.py`` file to only a few lines.

DMP still uses ``urls.py``, but it adds another URL resolver to Django's built in ones (such as the regex and path resolvers).  As explained in the tutorial, DMP resolves a url like ``/homepage/index/`` as follows:

-  The first url part ``homepage`` specifies the app that will be used.
-  The second url part ``index`` specifies the view or html page within the app. In our example:
-  The router first looks for ``homepage/views/index.py``. If it exists, it calls the ``process_request`` method in the file.
-  If ``index.py`` is not found, DMP looks for ``homepage/templates/index.html``.  If it exists, it renders the template directly using the Mako template system.



Install Django, Mako, and DMP
----------------------------------

DMP works with Django 1.9+, including the 2.0 releases.

The following will install all three dependencies:

::

    pip3 install django-mako-plus

(note that on Windows machines, ``pip3`` may need to be replaced with ``pip``)


Create a Vanilla Django Project
-------------------------------------

1. Create a DMP project.  You may want to follow the `standard Django Tutorial <https://docs.djangoproject.com/en/dev/intro/tutorial01/>`_ to create a ``mysite`` project.  Follow the tutorial through the section creating templates.

2. In your app directory (``/polls`` in the tutorial), switch from using a single views file to a package directory with the same name (DMP's router expects your views module to be a folder).

* Delete the ``views.py`` file.
* Create a new directory at ``/polls/views/``.
* Create a new file called ``/polls/views/__init__.py``.  The file can be empty (it doesn't need any content).

3. Add DMP to your installed apps in ``settings.py``:

.. code:: python

    INSTALLED_APPS = [
        ...
        'django_mako_plus',
        'polls',
    ]

4. Enable a logger in ``settings.py``. Routing problems can be solved much easier with DMP's debug messages:

.. code:: python

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'loggers': {
            'django_mako_plus': {
                'handlers': ['console_handler'],
                'level': DEBUG and 'DEBUG' or 'WARNING',
                'propagate': False,
            },
            'django': {
                'handlers': ['console_handler'],
                'level': 'INFO',
                'propagate': False,
            },
        },
        'handlers': {
            'console_handler': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
    }

5. Add DMP's router to ``urls.py``:

.. code:: python

    from django.conf.urls import path, include

    # this is Django 2.0 syntax
    urlpatterns = [
        path('', include('django_mako_plus.urls')),
    ]


Create an Endpoint
------------------------

1. Create a new file called ``polls/views/index.py``.  In this file, add the following content:

.. code:: python

    from django.shortcuts import render
    from django_mako_plus import view_function
    from datetime import datetime

    @view_function
    def process_request(request):
        context = {
            'now': datetime.now(),
        }
        return render(request, 'polls/index.html', context)

|

    Note the function is named ``process_request`` -- this is the default function that DMP looks for within the view file.

    Note also the ``@view_function`` decorator -- this security measure is required on every view function routed by DMP.


2. Create a template in ``polls/templates/polls/index.html``:

::

    <html>
    <body>
        The current time is {{ now|date:'c' }}
    </body>
    </html>



Run the project and go to `http://localhost:8000/polls/index/ <http://localhost:8000/polls/index/>`_.



Congratulations.  You've got a standard Django project that routes automagically using DMP's convention-based resolver.
