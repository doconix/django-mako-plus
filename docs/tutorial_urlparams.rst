T3: URL Parameters
===================================

.. contents::
    :depth: 2

Django is all about pretty URLs. In keeping with that philosophy, we present **URL parameters**. You've already used the beginning parts of the URL: the first specifies the app, the second specifies the view/template. **URL parameters are the third part, fourth part, and so on.**

In traditional web links, we specify parameters using key=value pairs, as in ``/homepage/index?product=144&model=A58UX``. That's ugly, and it's certainly not the Django way.

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

There are **several ways** to use DMP's URL parameters.   The following sections present the options, followed by our advice at the end.


request.urlparams
-------------------------------------------

    This first approach is not the preferred method, but it's a simple approach and introduces the idea best. Be sure to read further for the more preferred approaches.

DMP populates the ``request.urlparams[ ]`` list with all URL parts *after* the first two parts (``/homepage/index/``), up to the ``?`` (query string).  For example, the URL ``/homepage/index/144/A58UX/`` has two urlparams: ``144`` and ``A58UX``.  These can be accessed as ``request.urlparams[0]`` and ``request.urlparams[1]`` anywhere you have access to the request object.

The following table gives examples:

+--------------------------------------------------+-----------------------------------------------------------+
| ``/homepage/index/first/second/``                | ``request.urlparam = [ 'first', 'second' ]``              |
+--------------------------------------------------+-----------------------------------------------------------+
| ``/homepage/index/first/second``                 | ``request.urlparam = [ 'first', 'second' ]``              |
+--------------------------------------------------+-----------------------------------------------------------+
| ``/homepage/index/first//``                      | ``request.urlparam = [ 'first', '' ]``                    |
+--------------------------------------------------+-----------------------------------------------------------+
| ``/homepage/index``                              | ``request.urlparam = [ ]``                                |
+--------------------------------------------------+-----------------------------------------------------------+

In the examples above, the first and second URL result in the *same* list, even though the first URL has an ending slash.  The ending slash is optional and can be used to make the URL prettier.

    The ending slash is optional because DMP's default ``urls.py`` patterns ignore it.  If you define custom URL patterns instead of including the default ones, be sure to add the ending ``/?`` (unless you explicitly want the slash to be explicitly counted).



The Automated Way
--------------------------------

    Automatic parameter conversion was added in DMP 4.1.

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


Supported Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Out of the box, DMP converts the following types:

* ``str``: No conversion is necessary (the URL is already a string).
* ``int``: ``int(value)``
* ``float``: ``float(value)``
* ``bool``: ``value not in ('', '-', '0')`` (anything except these three strings is True)
* Model instance id: ``YourModel.objects.get(id=int(value))`` (uses the value as the id of the object)
* Anything else: ``raise ValueError`` (you can add more types--read on)


Booleans
##########################

In the example above, ``forward`` has a type hint *and* a default value, making it optional in the URL.  Consider how ``forward`` is evaluated in the following URLs:

+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30``     | Evaluates True because the third parameter is missing.  It is assigned the   |
|                                                   | default value of True (per the function signature).                          |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/-/``  | Evaluates False because the third parameter is a dash `-`.                   |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/%20/``| Evaluates True because the third parameter is a space (not one of the        |
|                                                   | False characters).                                                           |
+---------------------------------------------------+------------------------------------------------------------------------------+

While these conversion characters may seem a little arbitrary, these characters allow you to create "pretty" urls, with a dash or zero denoting False.


Django Models
################################

URL parameters are excellent places to specify ids of model objects.  For example, suppose the id for Purchase object #1501 is coded in a receipt page URL: ``http://localhost:8000/storefront/receipt/1501/``.  The following view function signature would automatically get the object from your database:

.. code:: python

    from django_mako_plus import view_function
    from storefront.models import Purchase

    @view_function
    def process_request(request, purchase:Purchase):
        # the `purchase` variable has already been pulled from the database

In the above code, one of two outcomes will occur:

* If a Purchase record with primary key 1501 exists in the database, it is sent into the function.
* If it doesn't exist, DMP raises Http404.

A third outcome could also have occurred if the URL had been slightly different.  In the URL ``http://localhost:8000/storefront/receipt/-/``, the purchase object would be ``None``, but the view function still would be called normally.  When converting Model parameters, the empty string, the dash, and a zero all cause the object to be None.  This allows your application to create URLs with objects explictily set to None.


Empty String == None
^^^^^^^^^^^^^^^^^^^^^^^^^^

In the Python language, the empty string and None have a special relationship.  The two are separate concepts with different meanings, but both evaluate to False, acting the same in the truthy statement: ``if not mystr:``.

Denoting "empty" parameters in the url is uncertain because:

1. Unless told otherwise, many web servers compact double slashes into single slashes. ``http://localhost:8000/storefront/receipt//second/`` becomes ``http://localhost:8000/storefront/receipt/second/``, preventing you from ever seeing the empty first paramter.
2. There is no real concept of "None" in a URL, only an empty string or some character *denoting* the absence of value.

Because of these difficulties, the urlparams list is programmed to never return None and never raise IndexError.  Even in a short URL with only a few parameters, accessing ``request.urlparams[50]`` returns an empty string.

For this reason, the default converters for booleans and Models objects equate the empty string *and* dash '-' as the token for False and None, respectively.  The single dash is especially useful because it provides a character in the URL (so your web server doesn't compact that position) and explicitly states the value.  Your custom converters can override this behavior, but be sure to check for the empty string in ``request.urlparams`` instead of ``None``.


Summary
------------------------

The point of this tutorial has been, "How do I get values from the URL into my view function?", and we discussed a number of approaches. Once converters are set up, view code is clean and straightforward because it generally involves simple type hints.

If you feel confused, consult the following table for advice:

+----------------------------------------------+---------------------------------------------------------------------------------------------+
| If your view function needs:                 | Then use this approach:                                                                     |
+==============================================+=============================================================================================+
| String values in the URL                     | `Add new parameters to your view function <The Automated Way_>`_.                           |
|                                              | No type hints or defaults are needed for strings.                                           |
+----------------------------------------------+---------------------------------------------------------------------------------------------+
| Integer, float, or boolean values,           | `Add type hints in your function signature <Adding Type Hints_>`_.                          |
| or Model object ids in the URL               | DMP will convert the URL values automatically.                                              |
+----------------------------------------------+---------------------------------------------------------------------------------------------+
| Values of other types in the URL             | See                                                                                         |
|                                              | `Extending the Default Converter <topics_urlparams.html#extending-the-default-converter>`_. |
+----------------------------------------------+---------------------------------------------------------------------------------------------+
| Your own, custom conversion process          | See                                                                                         |
|                                              | `Replacing the Default Converter <topics_urlparams.html#replacing-the-default-converter>`_. |
+----------------------------------------------+---------------------------------------------------------------------------------------------+
| Directly access the URL parts.               | Simply `access the request.urlparams list <request.urlparams_>`_ directly.                  |
+----------------------------------------------+---------------------------------------------------------------------------------------------+


For More Information
----------------------------

The `advanced topic on conversion <topics_urlparams.html>`_ expands the topics above.  Come back later if you want to continue the discussion on parameter conversion.