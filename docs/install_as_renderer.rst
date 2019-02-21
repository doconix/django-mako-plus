.. _install_as_renderer:

Using DMP to Render Mako Templates
=======================================

The following shows how to use DMP to render Mako templates only -- without any of DMP's other features.  It uses DMP as a normal template engine within a vanilla Django project.


Install Django, Mako, and DMP
----------------------------------

DMP works with Django 1.9+, including the 2.0 releases.

The following will install all three dependencies:

.. tabs::

   .. group-tab:: Linux/Mac

        .. code:: bash

            pip3 install --upgrade django-mako-plus

   .. group-tab:: Windows

        .. code:: powershell

            pip install --upgrade django-mako-plus


Create a Vanilla Django Project
-------------------------------------

1. Create a vanilla Django project.  You may want to follow the `standard Django Tutorial <https://docs.djangoproject.com/en/dev/intro/tutorial01/>`_ to create a ``mysite`` project.  Follow the tutorial through the section creating templates.

2. Create a basic view function in ``polls/views.py``:

.. code-block:: python

    from django.shortcuts import render
    from datetime import datetime

    def index(request):
        context = {
            'now': datetime.now(),
        }
        return render(request, 'polls/index.html', context)


3. Create a template in ``polls/templates/polls/index.html``:

.. code-block:: html+mako

    <html>
    <body>
        The current time is {{ now|date:'c' }}
    </body>
    </html>


4. Add a path in ``mysite/urls.py``:

.. code-block:: python

    from django.urls import url
    from polls import views

    urlpatterns = [
        url('', views.index, name='index'),
    ]


Run the project and go to `http://localhost:8000/ <http://localhost:8000/>`_.  Note that everything above is a normal Django project -- DMP isn't in play yet.


Enable the DMP Template Engine
----------------------------------

1. Add DMP to your installed apps in ``settings.py``.

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'django_mako_plus',
        'polls',
    ]

2. Add the DMP template engine in ``settings.py``.

.. code-block:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
        },
    ]

Note that we won't be using DMP to render templates.  But as a Django template engine, DMP initializes by being listed in ``TEMPLATES``.  We've listed DMP *after* the Django template renderer so Django can match and render templates first.

3. Enable a logger in ``settings.py`` to see DMP routing information and other messages:

.. code-block:: python

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


Create a View with Mako Syntax
-------------------------------------

Let's create a new endpoint that uses the Mako engine.  We'll leave the ``index`` endpoint as a Django template.

1. Add another endpoint to ``polls/views.py``:

.. code-block:: python

    from django.shortcuts import render
    from datetime import datetime

    def index(request):
        context = {
            'now': datetime.now(),
        }
        return render(request, 'polls/index.html', context)


    def another(request):
        context = {
            'now': datetime.now(),
        }
        return render(request, 'polls/another.html', context)


2. Create a Mako-syntax template in ``polls/templates/another.html``:

.. code-block:: html+mako

    <html>
    <body>
        The current time is ${ now.strftime('c') }
    </body>
    </html>

Note that your two templates are in **different folders**:

* ``mysite/polls/templates/polls/index.html``
* ``mysite/polls/templates/another.html``

See how the extra ``polls`` is missing in the DMP template?  That's because DMP template discovery algorithm is "app-aware".  When the view function specifies ``polls/another.html``, DMP interprets it using the pattern ``appname/templatename``.

The following code instructs DMP to go to the ``polls`` app and look for the ``another.html`` template.  Where Django would enumerate all your apps in search of the file, DMP looks for exactly one file path.

.. code-block:: python

    # goes directly to `polls/templates/another.html`
    render(request, 'polls/another.html', context)

We could adjust the DMP algorithm to match Django's locations, but the difference gives a nice separation when both Mako and Django templates exist in the same project.


3. Add a path in ``mysite/mysite/urls.py``:

.. code-block:: python

    from django.urls import path
    from polls import views

    # note this is Django 2.x syntax
    urlpatterns = [
        path('', views.index, name='index'),
        path('another', views.another, name='another'),
    ]


Run the project and go to `http://localhost:8000/another <http://localhost:8000/another>`_.

Congratulations.  You've got a standard Django project that can render Mako syntax.
