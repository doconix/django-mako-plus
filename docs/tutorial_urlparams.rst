T3: URL Parameters
===================================

.. contents::
    :depth: 2

Django is all about pretty URLs. In keeping with that philosophy, we present **URL parameters**. You've already used the beginning parts of the URL: the first specifies the app, the second specifies the view/template. **URL parameters are the third part, fourth part, and so on.**

In traditional web links, we specify parameters using key=value pairs, as in ``/homepage/index?product=144&model=A58UX``. That's ugly, and it's certainly not the Django way.

What About Django Path Converters?
--------------------------------------

One of the big changes in Django 2.0 (late 2017) is simplified URLs, including automatic parameter conversion. You might be wondering how the two relate to one another.

DMP first included automatic parameter conversion in early 2017, and it wasn't influenced by Django's design; the two developed separately.  DMP's parameter conversion is different in the following ways:

* DMP discovers parameters and type hints from your view function signatures; Django uses your patterns in ``urls.py``.
* Type hints and parameter defaults in DMP are specified the `standard Python way <https://docs.python.org/3/library/typing.html>`_.  Django uses a custom URL syntax.
* DMP has more built-in converters: DateTime, Decimal, all Django models, etc.
* Converters in DMP match using ``isinstance``; converters in Django match by regex match.

The conversion method in DMP matches well with its goal of convention-over-configuration.  Django's method matches well with its "enumerate all urls" design.  You can use both in the same project; DMP apps do it the DMP way, other apps do it the Django way.

At a Glance
---------------------

Compare the old vs. the new:

+--------------------------------------------------+------------------------------------------+
|  This:                                           | Becomes This:                            |
+==================================================+==========================================+
| ``/homepage/index?product=144&model=A58UX``      | ``/homepage/index/144/A58UX/``           |
|                                                  |                                          |
| * Longer                                         | * Shorter                                |
| * More difficult to text or email                | * Easier to text or email                |
| * Less search engine friendly                    | * More search engine friendly            |
| * A face only a programmer could love...         |                                          |
+--------------------------------------------------+------------------------------------------+

URL parameters don't take the place of form parameters. You'll still use GET and POST parameters to submit forms.  You'll still use name/value pairs when it makes sense, such as on a search page.  URL parameters are best used for object ids and other simple items that pages need to display, such as the product id in the previous example.
    
DMP sends "extra" parameters (``411`` and ``A58UX`` above) to your view function.  You only need to add variables for these parameters to your view function signature.  In addition, DMP automatically converts values into ``ints``, ``booleans``, and even your ``Models``. 


A New View Function Signature
------------------------------

Let's modify ``homepage/views/index.py`` to support adjusting the current date by a certain amount of time.  We'll specify the hours, minutes, and direction in the URL:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime, timedelta

    @view_function
    def process_request(request, hrs, mins, forward='+'):
        delta = timedelta(hours=int(hrs), minutes=int(mins))
        if forward == '+':
            now = datetime.now() + delta
        else:
            now = datetime.now() - delta
        context = {
            'now': now,
        }
        return request.dmp_render('index.html', context)


We'll use the ``homepage/templates/index.html`` file we created in previous tutorial parts:

.. code:: html

    <%inherit file="base.htm" />

    <%block name="content">
        <div class="content">
          <p class="server-time">The current server time is ${ now }.</p>
        </div>
    </%block>


Take your browser to http://localhost:8000/homepage/index/6/30/+.  It shows a time 6:30 in the future by evaluating the values in the URL.  Try different values to adjust the hours, minutes, and direction.

Since ``forward`` has a default value, it can be omitted: http://localhost:8000/homepage/index/6/30.

This first example shows how DMP sends URL parts into view functions.  It separates the URL parts by the slash ``/``, and positionally matches them to functions.  In this simplest of view function signatures, the parameters are strings.

    If you are using multiple decorators on your endpoints, you can save a lot of trouble by checking that your decorators `are wrapping correctly <topics_converters.html>`_.


Adding Type Hints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

But what if you need integers, booleans, or even Model instances, such as a User object, Purchase object, or Question object?  By adding type hints (yes, they're in the standard Python langauge), we can have them converted to the right type automatically.

Add the following type hints to your ``process_request`` function, and remove the typecasting calls:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime, timedelta

    @view_function
    def process_request(request, hrs:int, mins:int, forward:bool=True):
        delta = timedelta(hours=hrs, minutes=mins)
        if forward:
            now = datetime.now() + delta
        else:
            now = datetime.now() - delta
        context = {
            'now': now,
        }
        return request.dmp_render('index.html', context)

DMP casts the parameters by inspecting the method signature of ``process_request`` which specifies the parameter name, a color, and the type.  If a conversion error occurs, the default converter raises Http404.  All of this is configurable and extensible (read on).


Automatic Model Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DMP converts all of the Model classes in your project.   Suppose we have an model called ``storefront.Purchase``.  If we list this type as the type hint, DMP will pull the object from the database automatically:

.. code:: python

    from django_mako_plus import view_function
    from storefront.models import Purchase

    @view_function
    def process_request(request, purchase:Purchase):
        # the `purchase` variable has already been pulled from the database

In the above code, one of two outcomes will occur:

* If a Purchase record with primary key 1501 exists in the database, it is sent into the function.
* If it doesn't exist, DMP raises Http404.



For More Information
----------------------------

The `advanced topic on conversion <topics_converters.html>`_ expands the topics above.  Come back later if you want to continue the discussion on parameter conversion.