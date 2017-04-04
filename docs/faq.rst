Frequently Asked Questions
===============================

Where Is DMP Used?
------------------

This app was developed at MyEducator.com, primarily by `Dr. Conan C.
Albrecht <mailto:doconix@gmail.com>`_. Please email me if you find errors with this
tutorial or have suggestions/fixes. In addition to several production
web sites, I use the framework in my Django classes at BYU. 120+
students use the framework each year, and many have taken it to their
companies upon graduation. At this point, the framework is quite mature
and robust. It is fast and stable.

I've been told by some that DMP has a lot in common with Rails. When I
developed DMP, I had never used RoR, but good ideas are good ideas
wherever they are found, right? :)

Why Mako instead Django or Jinja2?
----------------------------------

Python has several mature, excellent templating languages. Both Django
and Jinja2 are fairly recent yet mature systems. Both are screaming
fast.

Mako itself is very stable, both in terms of "lack of bugs" and in
"completed feature set". Today, the Mako API almost never changes
because it does exactly what it needs to do and does it well. This make
it an excellent candidate for server use.

The short answer is I liked Mako's approach the best. It felt the most
Pythonic to me. Jinja2 may feel more like Django's built-in template
system, but Mako won out because it looked more like Python--and the
point of DMP is to include Python in templates.

Can I use DMP with regular Django apps?
-------------------------------------------

Yes. DMP plugs in as a regular templating engine per the standard Django
API.

The hook for most apps is the ``urls.py`` file. Just be sure that DMP's
line in this file comes *last*. DMP's line is a wildcard, so it matches
most urls. As long as the other app urls are listed first, Django will
give them preference.

Note also that other apps likely use Django's built-in templating system
rather than DMP's Mako templating system. The two templating systems
work fine side by side, so other apps should render fine the normal
Django way and your custom apps will render fine with Mako.

Further, if you temporarily need to switch to Django templating syntax,
`you can do that with
ease <#using-django-and-jinja2-tags-and-syntax>`__. This allows the use
of Django-style tags and syntax right within your Mako code. No new
files needed.
