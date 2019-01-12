About DMP
===========

.. contents::
    :depth: 3

Django-Mako-Plus makes creating web sites faster through **convention-over-configuration** in the Django framework.  It integrates the Mako templating engine, which looks much more like Python than the standard templating language. Yet it still conforms to the Django API and plugs in as a standard engine.



Frequently Asked Questions
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



Can I use DMP with regular Django apps?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. DMP plugs in as a regular templating engine per the standard Django API.  You can use both DMP and regular Django simultaneously in the same project.

When you include DMP's ``urls.py`` module in your project, patterns for each DMP-enabled app in your project are linked to our convention-based router.  Other apps won't match these patterns, so other apps route the normal Django way. This means third-party apps work just fine with DMP.


Can I use both Mako and Django/Jinja2 syntax?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes.  Django officially supports having two or more template engines active at the same time.  Third party apps likely use Django's templating system rather than Mako. The two templating systems work fine side by side.

If you temporarily need to switch to Django templating syntax (even within a Mako file), `you can do that too <#using-django-and-jinja2-tags-and-syntax>`_.






Comparison with Django
---------------------------------

If you have read through the Django Tutorial, you've seen examples for templating in Django. While the rest of Django, such as models, settings, migrations, etc., is the same with or without DMP, the way you do templates will obviously change with DMP. The following examples should help you understand the different between two template systems.

    Note that, for the most part, the right column uses standard Python syntax.  That's why Mako rocks.

+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| Django                                                                   | DMP (Mako)                                                            |
+==========================================================================+=======================================================================+
| **Output the value of the question variable:**                                                                                                   |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {{ question }}                                                       |     ${ question }                                                     |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Call a method on the User object:**                                                                                                            |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {{ user.get_full_name }}                                             |     ${ user.get_full_name() }                                         |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Call a method with parameters on the User object:**                                                                                            |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {# Requires a custom tag #}                                          |     ${ user.has_perm('app.get_main_view') }                           |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Iterate through a relationship:**                                                                                                              |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     <ul>                                                                 |     <ul>                                                              |
|         {% for choice in question.choice_set.all %}                      |         %for choice in question.choice_set.all():                     |
|             <li>{{ choice.choice_text }}</li>                            |             <li>${ choice.choice_text }</li>                          |
|         {% endfor %}                                                     |         %endfor                                                       |
|     </ul>                                                                |     </ul>                                                             |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Set a variable:**                                                                                                                              |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {% with name="Sam" %}                                                |     <% name = "Sam" %>                                                |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Format a date:**                                                                                                                               |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {{ value|date:"D d M Y" }}                                           |     ${ value.strftime('%D %d %M %Y') }                                |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Join a list:**                                                                                                                                 |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {{ mylist | join:', ' }}                                             |     ${ ', '.join(mylist) }                                            |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Use the /static prefix:**                                                                                                                      |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {% load static %}                                                    |     <img src="${ STATIC_ROOT }images/hi.jpg"/>                        |
|     <img src="{% get_static_prefix %}images/hi.jpg"/>                    |                                                                       |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Call a Python method:**                                                                                                                        |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {% Requires a custom tag, unless a    %}                             |     ## Any Python method can be called:                               |
|     {% built-in tag provides the behavior %}                             |     <%! import random %>                                              |
|                                                                          |     ${ random.randint(1, 10) }                                        |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Print a Django form:**                                                                                                                         |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     <form action="/your-name/" method="post">                            |     <form action="/your-name/" method="post">                         |
|         {% csrf_token %}                                                 |         ${ csrf_input }                                               |
|         {{ form }}                                                       |         ${ form }                                                     |
|         <input type="submit" value="Submit" />                           |         <input type="submit" value="Submit" />                        |
|     </form>                                                              |     </form>                                                           |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Output a default if empty:**                                                                                                                   |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {{ value | default:"nothing" }}                                      |     ## Use a boolean:                                                 |
|                                                                          |     ${ value or "nothing" }                                           |
|                                                                          |                                                                       |
|                                                                          |     ## or use a Python if statement:                                  |
|                                                                          |     ${ value if value is not None else "nothing" }                    |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
|     Run arbitrary Python:                                                                                                                        |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {# Requires a custom tag  #}                                         |     ## Keep it simple, Tex!                                           |
|                                                                          |     <%                                                                |
|                                                                          |         i = 1                                                         |
|                                                                          |         while i < 10:                                                 |
|                                                                          |             context.write('<p>Testing {0}</p>'.format(i))             |
|                                                                          |         i += 1                                                        |
|                                                                          |     %>                                                                |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Inherit another template:**                                                                                                                    |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {% extends "base.html" %}                                            |     <%inherit file="base.htm" />                                      |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Override a block:**                                                                                                                            |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {% block title %}                                                    |     <%block name="title">                                             |
|         My amazing blog                                                  |         My amazing blog                                               |
|     {% endblock %}                                                       |     </%block>                                                         |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Link to a CSS file:**                                                                                                                          |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {# Place in template #}                                              |     ## Automatically done by DMP (by name convention)                 |
|     <link rel="stylesheet" type="text/css" href="...">                   |                                                                       |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Perform per-request logic in JS files:**                                                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| .. code-block:: django                                                   | .. code-block:: html+mako                                             |
|                                                                          |                                                                       |
|     {# Difficult, young padwan...very difficult #}                       |     ## Wrap context keys with ``jscontext()``, and DMP will           |
|                                                                          |     ## make the variable available in your JS file.                   |
|                                                                          |                                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
