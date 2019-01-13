Frequently Asked Questions
=================================


General
-----------------------------


Where Is DMP Used?
^^^^^^^^^^^^^^^^^^^^^^^^

This app was developed at MyEducator.com, primarily by `Dr. Conan C. Albrecht <mailto:doconix@gmail.com>`_. Please email me if you find errors with this tutorial or have suggestions/fixes. In addition to several production web sites, I use the framework in my Django classes at BYU. 120+ students use the framework each year, and many have taken it to their companies upon graduation. At this point, the framework is quite mature and robust. It is fast and stable.

I've been told by some that DMP has a lot in common with Rails. When I developed DMP, I had never used RoR, but good ideas are good ideas wherever they are found, right? :)



What's wrong with Django's built-in template language?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Django comes with its own template system, but it's fairly weak (by design). Mako, on the other hand, is a fantastic template system that allows full Python code within HTML pages.

The primary reason Django doesn't allow full Python in its templates is the designers want to encourage you and I to keep template logic simple. I fully agree with this philosophy. I just don't agree with the "forced" part of this philosophy. The Python way is rather to give freedom to the developer but train in the correct way of doing things. Even though I fully like Python in my templates, I still keep them fairly simple. Views are where your logic goes.



Why Mako instead Django or Jinja2?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Python has several mature, excellent templating languages. Both Django and Jinja2 are fairly recent yet mature systems. Both are screaming fast.

Mako itself is very stable, both in terms of "lack of bugs" and in "completed feature set". Today, the Mako API almost never changes because it does exactly what it needs to do and does it well. This make it an excellent candidate for server use.

The short answer is I liked Mako's approach the best. It felt the most Pythonic to me. Jinja2 may feel more like Django's built-in template system, but Mako won out because it looked more like Python--and the point of DMP is to include Python in templates.

Will it bundle?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. DMP's providers automatically create entry files for template-related JS and CSS. See the `Tutorial </tutorial_css_js.html>`_ for how templates relate to their JS and CSS and `Webpack Providers </static_webpack.html>`_ for webpack-specific information.



Using Third-Party Apps
--------------------------------------------------


Does DMP work alonside third-party Django apps?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. DMP plugs in as a regular templating engine per the standard Django API.  You can use both DMP and regular Django simultaneously in the same project.

When you include DMP's ``urls.py`` module in your project, patterns for each DMP-enabled app in your project are linked to our convention-based router.  Other apps won't match these patterns, so other apps route the normal Django way. This means third-party apps work just fine with DMP.


How do I call a tag from a third-party app?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See the `integration docs </install_third_party>`_ for examples.


Can I use both Mako and Django/Jinja2 syntax?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes.  Django officially supports having two or more template engines active at the same time.  Third party apps likely use Django's templating system rather than Mako. The two templating systems work fine side by side.

If you temporarily need to switch to Django templating syntax (even within a Mako file), `you can do that too <#using-django-and-jinja2-tags-and-syntax>`_.



Logging
---------------------------------

Why is DMP is logging to the browser console?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The automatic inclusion of JS and CSS is a common trouble spot for new users of DMP, so we log debug information to both the Python and browser consoles.

You can turn this off by increasing the log level of DMP in settings.py:

.. code-block:: python

    'loggers': {
        'django_mako_plus': {
            'handlers': ['django_mako_plus_console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
