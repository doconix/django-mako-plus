Using DMP in Specific Apps
=======================================================

DMP normally enables itself within all "local" apps in your project.  That's the apps that are located beneath your project root.  It adds URL patterns for each of these apps when you ``include()`` it in ``urls.py``.

However, you can limit DMP to just one app or to a limited set of apps.

First, disable automatic app discovery in DMP's settings.py options:

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'APP_DISCOVERY': None,
            },
        },
        ...
    ]

Then explicitly register specific apps in your project with DMP.  For example, to allow DMP to route by convention and render templates within ``someapp``, add the following to ``someapp/apps.py``:

::

    from django.apps import AppConfig
    from django_mako_plus import register_app

    class SomeAppConfig(AppConfig):
        name = 'someapp'

        def ready(self):
            # explicitly tell DMP to control this app
            register_app(self)

Read more at `APP_DISCOVERY </basics_settings.html#app-discovery>`_.


Django vs DMP Router
-----------------------

DMP isn't special (don't tell it, though).  It simply adds a new URL resolver to the Django resolution sequence.

It's just a third-party app with some patterns ``urls.py``.  Integrating other libraries into your project is done the same way -- with entries in ``urls.py``, ``INSTALLED_APPS``, ``MIDDLEWARE``, and so forth.

In our best ASCII art, the following shows two DMP apps and two "normal" apps:

::

    urls.py  --+-- /app1/* -->  DMP router  -->  app1/views/page1.py::process_request()
               |   /app2/*                       app1/views/page2.py::process_request()
               |                                 app2/views/page1.py::process_request()
               |                                 app2/views/page2.py::process_request()
               |                                 ...
               |
               +-- /app3/page1/ --> app3/views.py::page1()
               +-- /app3/page2/ --> app3/views.py::page2()
               |
               +-- /app4/page1/ --> app4/views.py::page1()
               +-- /app4/page2/ --> app4/views.py::page2()

In the above diagram, DMP's wildcards in ``urls.py`` take control of all pages within the "DMP-enabled" apps and allow explicit entries to route other apps.

You can read more about routing over in the `Django docs <https://docs.djangoproject.com/en/dev/topics/http/urls/>`_.


Pattern Order
~~~~~~~~~~~~~~~~~~~~~~~~~~

``tl;dr`` Put DMP's include as the last entry in ``urls.py``.

Nearly as short version: Django matches the patterns in ``urls.py`` in order--top to bottom.  Since DMP's patterns contain wildcards, they are a bit greedy.  If the DMP include is one of the first patterns listed, it may not let a third party library control needed url patterns.  By listing DMP last in the list of patterns, you'll allow explicit pattern-to-view directives to occur.

If you are using a third-party libraries that also have greedy, wildcard-driven patterns, you may need to play a bit with order in ``urls.py``.
