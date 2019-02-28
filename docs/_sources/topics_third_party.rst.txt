.. _topics_third_party:

Using Third-Party Apps
=======================================================

One of the greatest strengths of Django is the wealth of third-party apps available through ``pip``. A few examples of popular apps are:

* `django-extensions <https://django-extensions.readthedocs.io/en/latest/>`_
* `Django Rest Framework <https://www.django-rest-framework.org/>`_
* `Crispy Forms <http://django-crispy-forms.readthedocs.io/>`_
* `Wagtail CMS <https://wagtail.io/>`_
* `Many, many more <https://djangopackages.org/>`_

Have no fear, DMP works together with them just like an integration of Windows and Linux!  (just kidding, they work fine together.)  Read on for a few things to watch for.

Third-Party URL Patterns
----------------------------

It is important to include *third-party url patterns/includes first* in ``urls.py``. DMP's url patterns are wildcards, so they need to be listed last or they'll take over everything.

But be assurred that DMP's url patterns follow the standards, so they play nicely with the other apps in ``urls.py``.


Third-Party Tags
----------------------------

Third-party apps often come with custom Django tags that you include in templates.  Since those tags are likely in Django format (and not Mako), you'll have to slightly translate the documentation for each library.

Method 1: Call the Tag Directly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In most cases, third-party tags are just functions within the third-party library. Just call the function directly.

For example, here's how to use the custom form tag in the `Django Paypal App <http://django-paypal.readthedocs.io/>`_:

+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| Django Paypal App in a Django template                                   | Django Paypal App in a DMP template                                   |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {{ form.render }}                                                    |     ${ form.render() }                                                |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+

Note the parenthases in the DMP code (it's a function call, after all).


Method 2: Skip the Tag Altogether
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the tag can't be called using regular Python, take a look at the third-party code. What does the tag actually do?  In most libraries, tags are just fronts for regular library functions (since Django doesn't allow direct Python in templates--talk about a manufactured problem...). If so, you can skip the tag and call the embedded function directly.

Even when third-party tags contain functionality directly, libraries usually provide mirror functions for calling from regular Python views.

For example, to use the `Crispy Form library <http://django-crispy-forms.readthedocs.io/>`_, simply import and call its ``render_crispy_form`` function directly:

+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| Crispy Forms in a Django template                                        | Crispy Forms in a DMP template                                        |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {% load crispy_forms_tags %}                                         |     <%! from crispy_forms.utils import render_crispy_form %>          |
|                                                                          |                                                                       |
|     <form method="post">                                                 |     <form method="post">                                              |
|         {{ form | crispy }}                                              |         ${ render_crispy_form(form) }                                 |
|     </form>                                                              |     </form>                                                           |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+


If you call a function like ``render_crispy_form`` often, you may want to `add it as a global template import <topics_modules.html>`_.


Method 3: Use as Directed...Django Syntax
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There may be times when you have no choice but to call a third-party tag the way it was designed: with Django syntax. DMP templates can include Django syntax blocks, even though it's a little kludgy to do so. But be assured that when needed, tags can be used exactly as the third-party documentation describes.

Venture over to `Django Syntax and Tags </topics_other_syntax.html>`_ to get schooled.
