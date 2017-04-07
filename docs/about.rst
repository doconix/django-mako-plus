About DMP
===========

.. contents::
    :depth: 3

Django-Mako-Plus makes creating web sites faster through **convention-over-configuration** in the Django framework.  It integrates the Mako templating engine, which looks much more like Python than the standard templating language. Yet it still conforms to the Django API and plugs in as a standard engine.

DMP boasts the following advantages:

1. It uses the **Mako templating engine** rather than the weaker Django templating engine. Why would I want to learn a whole new language for templating when Mako uses my favorite language: Python?

2. It enables **calling views and html pages by convention** rather than specific entries in urls.py. Any .html file on your site can be called without new entries in urls.py for every. single. new. page. Doesn't Python favor convention over configuration?

3. DMP introduces the idea of URL parameters. These allow you to embed parameters in urls, Django style--meaning you can use pretty URLs like http://myserver.com/abc/def/123/ **without explicit entries in urls.py** and without the need for traditional (i.e. ulgy) ?first=abc&second=def&third=123 syntax.

4. It separates view functions into different files rather than all-in-one style. Anyone who has programmed Django long knows that the single views.py file in each app often gets looooonnng. Splitting logic into separate files keeps things more orderly.

5. It includes CSS and JS files automatically, and it allows Python code within these files. These static files get included in your web pages without any explicit declaration of ``<link>`` or ``<script>`` elements. This means that ``mypage.css`` and ``mypage.js`` get linked in ``mypage.html`` automatically. Python code within these support files means your CSS can change based on user or database entries.

6. Optionally, it integrates with Sass by automatically running ``scss`` on updated .scss files.


    **Author's Note:** Django comes with its own template system, but it's fairly weak (by design). Mako, on the other hand, is a fantastic template system that allows full Python code within HTML pages. The primary reason Django doesn't allow full Python in its templates is the designers want to encourage you and I to keep template logic simple. I fully agree with this philosophy. I just don't agree with the "forced" part of this philosophy. The Python way is rather to give freedom to the developer but train in the correct way of doing things. Even though I fully like Python in my templates, I still keep them fairly simple. Views are where your logic goes.


Frequently Asked Questions
-----------------------------


Where Is DMP Used?
^^^^^^^^^^^^^^^^^^^^^^^^

This app was developed at MyEducator.com, primarily by `Dr. Conan C. Albrecht <mailto:doconix@gmail.com>`_. Please email me if you find errors with this tutorial or have suggestions/fixes. In addition to several production web sites, I use the framework in my Django classes at BYU. 120+ students use the framework each year, and many have taken it to their companies upon graduation. At this point, the framework is quite mature and robust. It is fast and stable.

I've been told by some that DMP has a lot in common with Rails. When I developed DMP, I had never used RoR, but good ideas are good ideas wherever they are found, right? :)

Why Mako instead Django or Jinja2?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Python has several mature, excellent templating languages. Both Django and Jinja2 are fairly recent yet mature systems. Both are screaming fast.

Mako itself is very stable, both in terms of "lack of bugs" and in "completed feature set". Today, the Mako API almost never changes because it does exactly what it needs to do and does it well. This make it an excellent candidate for server use.

The short answer is I liked Mako's approach the best. It felt the most Pythonic to me. Jinja2 may feel more like Django's built-in template system, but Mako won out because it looked more like Python--and the point of DMP is to include Python in templates.

Can I use DMP with regular Django apps?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. DMP plugs in as a regular templating engine per the standard Django API.

The hook for most apps is the ``urls.py`` file. Just be sure that DMP's line in this file comes *last*. DMP's line is a wildcard, so it matches most urls. As long as the other app urls are listed first, Django will give them preference.

Note also that other apps likely use Django's built-in templating system rather than DMP's Mako templating system. The two templating systems work fine side by side, so other apps should render fine the normal Django way and your custom apps will render fine with Mako.

Further, if you temporarily need to switch to Django templating syntax, `you can do that with ease <#using-django-and-jinja2-tags-and-syntax>`__. This allows the use of Django-style tags and syntax right within your Mako code. No new files needed.






Comparison with Django
---------------------------------

If you have read through the Django Tutorial, you've seen examples for templating in Django. While the rest of Django, such as models, settings, migrations, etc., is the same with or without DMP, the way you do templates will obviously change with DMP. The following examples should help you understand the different between two template systems.

    Note that, for the most part, the right column uses standard Python syntax.  That's why Mako rocks.

+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| Django                                                                   | DMP (Mako)                                                            |
+==========================================================================+=======================================================================+
| **Output the value of the question variable:**                                                                                                   |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | {{ question }}                                                         | | ${ question }                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Call a method on the User object:**                                                                                                            |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | {{ user.get_full_name }}                                               | | ${ user.get_full_name() }                                           |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Call a method with parameters on the User object:**                                                                                            |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| Requires a custom tag.                                                   | | ${ user.has_perm('app.get_main_view') }                             |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Iterate through a relationship:**                                                                                                              |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | <ul>                                                                   | | <ul>                                                                |
| |   {% for choice in question.choice_set.all %}                          | |   %for choice in question.choice_set.all():                         |
| |     <li>{{ choice.choice_text }}</li>                                  | |     <li>${ choice.choice_text }</li>                                |
| |   {% endfor %}                                                         | |   %endfor                                                           |
| | </ul>                                                                  | | </ul>                                                               |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Set a variable:**                                                                                                                              |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | {% with name="Sam" %}                                                  | | <% name = "Sam" %>                                                  |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Format a date:**                                                                                                                               |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | {{ value|date:"D d M Y" }}                                             | | ${ value.strftime('%D %d %M %Y') }                                  |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Join a list:**                                                                                                                                 |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | {{ mylist | | join:', ' }}                                             | | ${ ', '.join(mylist) }                                              |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Use the /static prefix:**                                                                                                                      |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | {% load static %} <img src="{% get_static_prefix %}images/hi.jpg"/>    | | <img src="${ STATIC_ROOT }images/hi.jpg"/>                          |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Call a Python method:**                                                                                                                        |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| Requires a custom tag, unless a built-in tag provides the behavior.      | Any Python method can be called:                                      |
|                                                                          | |   <%! import random %>                                              |
|                                                                          | |   ${ random.randint(1, 10) }                                        |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Print a Django form:**                                                                                                                         |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | <form action="/your-name/" method="post">                              | | <form action="/your-name/" method="post">                           |
| |   {% csrf_token %}                                                     | |   ${ csrf_input }                                                   |
| |   {{ form }}                                                           | |   ${ form }                                                         |
| |   <input type="submit" value="Submit" />                               | |   <input type="submit" value="Submit" />                            |
| | </form>                                                                | | </form>                                                             |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Output a default if empty:**                                                                                                                   |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | {{ value | | default:"nothing" }}                                      | Use a boolean:                                                        |
|                                                                          | | ${ value or "nothing" }                                             |
|                                                                          | or use a Python if statement:                                         |
|                                                                          | | ${ value if value != None else "nothing" }                          |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | Run arbitrary Python (keep it simple, Tex!):                                                                                                   |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| Requires a custom tag                                                    | | <%                                                                  |
|                                                                          | |   i = 1                                                             |
|                                                                          | |     while i < 10:                                                   |
|                                                                          | |       context.write('<p>Testing {0}</p>'.format(i))                 |
|                                                                          | |     i += 1 %>                                                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Inherit another template:**                                                                                                                    |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | {% extends "base.html" %}                                              | | <%inherit file="base.htm" />                                        |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Override a block:**                                                                                                                            |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| | {% block title %}My amazing blog{% endblock %}                         | | <%block name="title">My amazing blog</%block>                       |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Link to a CSS file:**                                                                                                                          |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| Place in template:                                                       | Simply name the .css/.js file the same name as your .html template.   |
| |  <link rel="stylesheet" type="text/css" href="...">                    | DMP will include the link automatically.                              |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| **Perform per-request logic in CSS or JS files:**                                                                                                |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
| Create an entry in urls.py, create a view,                               | Simply name the .css file as name.cssm for each name.html template.   |
| and render a template for the CSS or JS.                                 | DMP will render the template and include it automatically.            |
+--------------------------------------------------------------------------+-----------------------------------------------------------------------+
