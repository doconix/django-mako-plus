Third-Party Apps
=======================================================

Since most third-party apps use standard Django routing and template syntax, new users to DMP often worry about conflicts between the two engines.  Have no fear, they work together just like Windows and Linux!  (just kidding, they work great together)

The most straightforward way to use DMP with third-party apps is to use only one template engine per app.  Some of your apps can be DMP-style, and others can be Django-style.  However, you can even mix the two when needed.

``urls.py``
---------------------

Integrating third-party apps into DMP is more obvious when you see what DMP's router really is.  You already know that DMP routes using a convention: the ``/app/page`` format.  This is different from Django, which explicitly includes an entry for each view in ``urls.py``.  You might think DMP modifies Django's built-in router.  But not so -- it's turtles all the way down... :)

In reality, DMP's router is a **secondary router** that comes **after** urls.py has already done its job.  DMP's router is really a *view function*.  DMP's patterns in ``urls.py`` send all requests for your DMP-registered apps to a single view function.  DMP then further routes, based on its convention, to your view function.  This simplifies the process a bit, but the essence is we have two routers: Django and then DMP.

DMP isn't special (don't tell it, though).  It's just a third-party app with some patterns ``urls.py``.  Integrating other libraries into your project is done the same way -- with entries in ``urls.py``, ``INSTALLED_APPS``, ``MIDDLEWARE``, and so forth.

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

``tl;dr`` Put DMP's include as the last in ``urls.py``.

Nearly as short version: Django matches the patterns in ``urls.py`` in order--top to bottom.  Since DMP's patterns contain wildcards, they are a bit greedy.  If the DMP include is one of the first patterns listed, it may not let a third party library control needed url patterns.  By listing DMP last in the list of patterns, you'll allow explicit pattern-to-view directives to occur.

If you are using a third-party libraries that also have greedy, wildcard-driven patterns, you may need to play a bit with order in ``urls.py``.


Which apps haz DMP?
--------------------------

In ``urls.py``, DMP adds patterns for all "DMP-registered" apps.  It's patterns are greedy, so they route most everything within these apps.

*But what, exactly, is a "DMP-registered" app?*

DMP needs to know which apps it routes for and which it should leave alone.  This is done through app registration with DMP.  This is normally done automatically at system startup, but you can register any app manually.  To explicitly register ``someapp``, add the following to ``someapp/apps.py``:

::

    from django.apps import AppConfig
    from django_mako_plus import register_dmp_app

    class SomeAppConfig(AppConfig):
        name = 'someapp'

        def ready(self):
            # explicitly tell DMP to control this app
            register_dmp_app(self)

DMP normally does the above automatically at startup.  The ``APP_DISCOVERY`` variable in settings.py determines which apps DMP automatically registers:

- ``default`` - The apps in your local project folder are registered at system startup.  Normally, these are the apps you've created.  This is, as you might have figured out, the default behavior.
- ``none`` - Automatic registration is disabled.  You'll need to manually register apps with DMP (see the above example).  This is useful when you have a mix of DMP apps and "regular" apps.
- ``all`` - DMP registers **every** app in ``INSTALLED_APPS``, including the built-in ``/admin/`` and third-party libraries.  Yeah, don't use this setting.

(see also `APP_DISCOVERY </basics_settings.html#app-discovery>`_)

Calling Third-Party Apps
-----------------------------------

Third-party apps often come with custom Django tags that you include in templates.  Since those tags are likely in Django format (and not Mako), you'll have to slightly translate the documentation for each library.

In most cases, third-party functions can be called directly from Mako. For example, the custom form tag in the `Django Paypal library <http://django-paypal.readthedocs.io/>`_ converts easily to Mako syntax:

-  The docs show: ``{{ form.render }}``
-  You use: ``${ form.render() }``

In the above example, we're simply using regular Python in DMP to call the tags and functions within the third party library.

If the tag can't be called using regular Python, you can usually inspect the third-party tag code.  In most libraries, tags just call Python functions because since Django doesn't allow direct Python in templates.  In the `Crispy Form library <http://django-crispy-forms.readthedocs.io/>`_, you can simply import and call its ``render_crispy_form`` function directly.  This skips over the Django tag entirely:

::

    <%! from crispy_forms.utils import render_crispy_form %>

    <html>
    <body>
        <form method="POST">
            ${ csrf_input }
            ${ render_crispy_form(form) }
        </form>
    </body>
    </html>


If you call the ``render_crispy_form`` method in many templates, you may want to add the import to ``DEFAULT_TEMPLATE_IMPORTS`` in your ``settings.py`` file. Once this import exists in your settings, the function will be globally available in every template on your site.

    Whenever you modify the DMP settings, be sure to clean out your cached templates with ``python3 manage.py dmp cleanup``. This ensures your compiled templates are rebuilt with the new settings.


Using Third-Party Tags
------------------------------

There may be times when you can't call a third-party function.  Or perhaps you just want to use the Django tags as the third-party library intended, dammit!

Venture over to `Django Syntax and Tags </topics_other_syntax.html>`_ to see how to include Django-style tags in your Mako templates.
