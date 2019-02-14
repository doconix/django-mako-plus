T3: URL Parameters
===================================

.. contents::
    :depth: 2

Django is `a little vain about pretty URLs <https://docs.djangoproject.com/en/dev/topics/http/urls/>`_. In keeping with that philosophy, we present **URL parameters**. You've already used the beginning parts of the URL: the first specifies the app, the second specifies the view/template. **URL parameters are the third part, fourth part, and so on.**

In traditional web links, we specify parameters using key=value pairs, as in ``/homepage/index?product=144&model=A58UX``. That's not the Django way.

This isn't just about pretty URLs. It's functional: DMP automatically converts URL-coded data into view function parameters. Mmmm. Parameter conversion, right out of the box.

What About Django Path Converters?
    One of the big changes in Django 2.0 (late 2017) is `simplified URLs and path converters <https://docs.djangoproject.com/en/dev/topics/http/urls>`_. You might be wondering how the two are related. DMP first included automatic parameter conversion in early 2017, and it wasn't influenced by Django's design; the two developed separately.  DMP's parameter conversion is different in the following ways:

    * DMP discovers parameters and type hints from your view function signatures; Django uses your patterns in ``urls.py``.
    * Type hints and parameter defaults in DMP are specified the `standard Python way <https://docs.python.org/3/library/typing.html>`_.  Django uses a custom format.
    * DMP has more built-in converters: DateTime, Decimal, all Django models, etc.
    * Converters in DMP match using ``isinstance``; converters in Django match by regex.

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
| * More difficult to text or email                | * Easier to bookmark and copy            |
| * Less search engine friendly                    | * More search engine friendly            |
| * A face only a mother could love...             |                                          |
+--------------------------------------------------+------------------------------------------+

DMP sends "extra" parameters (``411`` and ``A58UX`` above) to your view function.  Just modify your view function signature and drop the mic.  In addition, DMP converts values into ``ints``, ``booleans``, and even into ``Model`` objects.

    URL parameters don't take the place of form parameters. You'll still use GET and POST parameters to submit forms.  You'll still use name/value pairs when it makes sense, such as on a search page.  URL parameters are best used for object ids and other simple items that pages need to display, such as the product id in the previous example.


A New View Function Signature
------------------------------

Let's modify ``homepage/views/index.py`` to support adjusting the current date by a certain amount of time.  We'll specify the hours, minutes, and direction in the URL:

.. code-block:: python

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
        return request.dmp.render('index.html', context)


We'll use the ``homepage/templates/index.html`` file we created in previous tutorial parts:

.. code-block:: html+mako

    <%inherit file="base.htm" />

    <%block name="content">
        <div class="content">
          <p class="server-time">The current server time is ${ now }.</p>
        </div>
    </%block>


Take your browser to http://localhost:8000/homepage/index/6/30/+.  It shows a time 6:30 in the future by evaluating the values in the URL.  Try different values to adjust the hours, minutes, and direction.

Since ``forward`` has a default value, it can be omitted: http://localhost:8000/homepage/index/6/30.

This first example shows how DMP sends URL parts into view functions.  It separates the URL parts by the slash ``/``, and positionally matches them to functions.  In this simplest of view function signatures, the parameters are strings.

    If you are using multiple decorators on your endpoints, you can save a lot of trouble by checking that your decorators `are wrapping correctly <converters_decorators.html>`_.

Automatic Type Converters
----------------------------

DMP can also typecast the values in the URL.  The following table shows the built-in types to DMP:

+-------------------------------+-------------------------------------------------------------------------------+---------------------------------------+-------------------------------------------+
|  Type                         | Example view.py functions                                                     | Example URLs                          | Notes                                     |
+===============================+===============================================================================+=======================================+===========================================+
| String (default type)         | | def process_request(request, foo):                                          | /homepage/index/hello+world/          | No preset empty values on strings;        |
|                               | |                                                                             |                                       | default is only used when parameter is    |
|                               | | def process_request(request, foo="bar"):                                    |                                       | missing (e.g. /homepage/index/)           |
|                               | |                                                                             |                                       |                                           |
|                               | | def process_request(request, foo:str):                                      |                                       |                                           |
|                               | |                                                                             |                                       |                                           |
|                               | | def process_request(request, foo:str="bar"):                                |                                       |                                           |
+-------------------------------+-------------------------------------------------------------------------------+---------------------------------------+-------------------------------------------+
| Integer                       | | def process_request(request, foo:int):                                      | /homepage/index/42/                   | "empty" values are '', '-' (uses default) |
|                               | |                                                                             |                                       |                                           |
|                               | | def process_request(request, foo:int=13):                                   |                                       |                                           |
|                               | |                                                                             |                                       |                                           |
|                               | | def process_request(request, foo:int="13"):                                 |                                       |                                           |
+-------------------------------+-------------------------------------------------------------------------------+---------------------------------------+-------------------------------------------+
| Float                         | | def process_request(request, foo:float):                                    | /homepage/index/32.275/               | "empty" values are '', '-' (uses default) |
|                               | |                                                                             |                                       |                                           |
|                               | | def process_request(request, foo:float=3.14):                               |                                       |                                           |
|                               | |                                                                             |                                       |                                           |
|                               | | def process_request(request, foo:float="3.14"):                             |                                       |                                           |
+-------------------------------+-------------------------------------------------------------------------------+---------------------------------------+-------------------------------------------+
| Boolean                       | | def process_request(request, foo:bool):                                     | /homepage/index/1/                    | False values are 'f', 'F', '0';           |
|                               | |                                                                             |                                       | "empty" values are '', '-' (uses default);|
|                               | | def process_request(request, foo:bool=True)                                 |                                       | True is anything else                     |
|                               | |                                                                             |                                       |                                           |
|                               | | def process_request(request, foo:bool='t')                                  |                                       |                                           |
+-------------------------------+-------------------------------------------------------------------------------+---------------------------------------+-------------------------------------------+
| Decimal                       | | from decimal import Decimal                                                 | /homepage/index/32.275/               | "empty" values are '', '-' (uses default) |
|                               | | def process_request(request, foo:Decimal):                                  |                                       |                                           |
|                               | |                                                                             |                                       |                                           |
|                               | | from decimal import Decimal                                                 |                                       |                                           |
|                               | | def process_request(request, foo:Decimal=Decimal('3.14')):                  |                                       |                                           |
|                               | |                                                                             |                                       |                                           |
|                               | | from decimal import Decimal                                                 |                                       |                                           |
|                               | | def process_request(request, foo:Decimal='3.14'):                           |                                       |                                           |
+-------------------------------+-------------------------------------------------------------------------------+---------------------------------------+-------------------------------------------+
| DateTime                      | | from datetime import datetime                                               | /homepage/index/1993-04-30+06:00:00/  | Uses formats listed in                    |
|                               | | def process_request(request, foo:datetime):                                 |                                       | DATETIME_INPUT_FORMATS from settings.py;  |
|                               | |                                                                             |                                       | "empty" values are '', '-' (uses default) |
|                               | | from datetime import datetime                                               |                                       |                                           |
|                               | | def process_request(request, foo:datetime=datetime(1993, 04, 30, 6, 0, 0)): |                                       |                                           |
|                               | |                                                                             |                                       |                                           |
|                               | | from datetime import datetime                                               |                                       |                                           |
|                               | | def process_request(request, foo:datetime='1993-04-30+06:00:00'):           |                                       |                                           |
+-------------------------------+-------------------------------------------------------------------------------+---------------------------------------+-------------------------------------------+
| Date                          | | from datetime import date                                                   | /homepage/index/1983-01-01/           | Uses formats listed in                    |
|                               | | def process_request(request, foo:date):                                     |                                       | DATE_INPUT_FORMATS from settings.py       |
|                               | |                                                                             |                                       | "empty" values are '', '-' (uses default) |
|                               | | from datetime import date                                                   |                                       |                                           |
|                               | | def process_request(request, foo:date=date(1983, 1, 1)):                    |                                       |                                           |
|                               | |                                                                             |                                       |                                           |
|                               | | from datetime import date                                                   |                                       |                                           |
|                               | | def process_request(request, foo:date='1983-01-01'):                        |                                       |                                           |
+-------------------------------+-------------------------------------------------------------------------------+---------------------------------------+-------------------------------------------+
| All model.Model subclasses    | | from django.contrib.auth.models import User                                 | /homepage/index/5/                    | Value is the id of the model object;      |
| (see below)                   | | def process_request(request, user:User):                                    |                                       | Http404 raised if not found;              |
|                               | |                                                                             |                                       | "empty" values are '', '-', '0'           |
|                               | | from polls.models import Question                                           |                                       | (uses default)                            |
|                               | | def process_request(request, question:Question):                            |                                       |                                           |
|                               | |                                                                             |                                       |                                           |
|                               | | from polls.models import Choice                                             |                                       |                                           |
|                               | | def process_request(request, choice:Choice=None):                           |                                       |                                           |
+-------------------------------+-------------------------------------------------------------------------------+---------------------------------------+-------------------------------------------+


Adding Type Hints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In your example code, add the following type hints to your ``process_request`` function, and remove the typecasting calls:

.. code-block:: python

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
        return request.dmp.render('index.html', context)

DMP casts the parameters by inspecting the method signature of ``process_request`` which specifies the parameter name, a color, and the type.  If a conversion error occurs, the default converter raises Http404.  All of this is configurable and extensible (read on).



Automatic Model Conversion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DMP converts all of the Model classes in your project.   Suppose we have an model called ``storefront.Purchase``.  If we list this type as the type hint, DMP will pull the object from the database automatically:

.. code-block:: python

    from django_mako_plus import view_function
    from storefront.models import Purchase

    @view_function
    def process_request(request, purchase:Purchase):
        # the `purchase` variable has already been pulled from the database

In the above code, one of two outcomes will occur:

* If a Purchase record with primary key 1501 exists in the database, ``Purchase.objects.get(id=...)`` is called automatically, and the purchase is sent into the view function.
* If it doesn't exist, DMP raises Http404.



For More Information
----------------------------

There's lots more to discover at `the pages on conversion <converters.html>`_.
