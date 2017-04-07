T3: URL Parameters
===================================


Django is all about pretty URLs. In keeping with that philosophy, this framework has URL parameters. We've already used the first two items in the path: the first specifies the app, the second specifies the view/template. URL parameters are the third part, fourth part, and so on.

In traditional web links, you'd specify parameters using key=value pairs, as in ``/homepage/index?product=144&model=A58UX``. That's ugly, and it's certainly not the Django way.

At a Glance
---------------------

The following compares the normal name/value pairs with DMP's new-and-improved way:

+--------------------------------------------------+------------------------------------------+
|  This:                                           | Becomes This:                            |
+==================================================+==========================================+
| ``/homepage/index?product=144&model=A58UX19-E``  | ``/homepage/index/144/A58UX/``           |
|                                                  |                                          |
| * Longer                                         | * Shorter                                |
| * More difficult to text or email                | * Easier to text or email                |
| * Less search engine friendly                    | * More search engine friendly            |
| * Only a programmer could love...                |                                          |
+--------------------------------------------------+------------------------------------------+

    Note that URL parameters don't take the place of form parameters. You'll still use GET and POST parameters to submit forms.  You'll still use name/value pairs when it makes sense, such as on a search page.  URL parameters are best used for object ids and other simple items that pages need to display, such as the product id in the previous example.


There are, essentially, **two ways** to use DMP's URL parameters.   The first approach is the ``request.urlparams`` list.  The second is automatic parameter matching and conversion for the view function.


Approach 1: request.urlparams
-------------------------------------------

    This first approach is not the preferred method, but it's a simple approach that can be explained quickly.  Let's get it out of the way first.

DMP populates the ``request.urlparams[ ]`` list with all URL parts *after* the first two parts (``/homepage/index/``), up to the ``?`` (query string).  For example, the URL ``/homepage/index/144/A58UX/`` has two urlparams: ``144`` and ``A58UX``.  These can be accessed as ``request.urlparams[0]`` and ``request.urlparams[1]`` anywhere you have access to the request object.

The following table gives examples; note that an ending slash creates an extra, empty item in the list.

+--------------------------------------------------+-----------------------------------------------------------+
| ``/homepage/index/first/second/``                | ``request.urlparam = [ 'first', 'second', '' ]``          |
+--------------------------------------------------+-----------------------------------------------------------+
| ``/homepage/index/first/second``                 | ``request.urlparam = [ 'first', 'second' ]``              |
+--------------------------------------------------+-----------------------------------------------------------+
| ``/homepage/index/first//``                      | ``request.urlparam = [ 'first', '', '' ]``                |
+--------------------------------------------------+-----------------------------------------------------------+
| ``/homepage/index``                              | ``request.urlparam = [ ]``                                |
+--------------------------------------------------+-----------------------------------------------------------+
| ``/homepage/index/``                             | ``request.urlparam = [ '', ]``                            |
+--------------------------------------------------+-----------------------------------------------------------+


Approach 2: The Automated Way
--------------------------------

On to the preferred approach...

Let's modify ``homepage/views/index.py`` to support adjusting the current date by a certain amount of time.  We'll specify the hours, minutes, and direction in the URL:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime, timedelta
    from .. import dmp_render, dmp_render_to_string

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
        return dmp_render(request, 'index.html', context)


We'll use the ``homepage/templates/index.html`` file we created in previous tutorial parts:

.. code:: html

    <%inherit file="base.htm" />

    <%block name="content">
        <div class="content">
          <p class="server-time">The current server time is ${ now }.</p>
        </div>
    </%block>


Take your browser to `http://localhost:8000/homepage/index/6/30/+ <http://localhost:8000/homepage/index/6/30/+>`_.  It shows a time 6:30 in the future by evaluating the values in the URL.  Try different values to adjust the hours, minutes, and direction.

Since the ``forward`` parameter has a default value, it can be omitted: `http://localhost:8000/homepage/index/6/30 <http://localhost:8000/homepage/index/6/30>`_ if needed.

This first example shows how DMP sends URL parts into view functions.  It separates the URL parts by the slash ``/``, and positionally matches them to functions.  In this simplest of view function signatures, the parameters are strings.



Adding Type Hints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

But what if you need integers, booleans, or even Model instances, such as a User object, Purchase object, or Question object?  By adding type hints (yes, they're in the standard Python langauge), we can have them converted to the right type automatically.

Add the following type hints to your ``process_request`` function, and remove the typecasting calls:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime, timedelta
    from .. import dmp_render, dmp_render_to_string

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
        return dmp_render(request, 'index.html', context)

DMP casts the parameters by inspecting the method signature of ``process_request`` which specifies the parameter name, a color, and the type.  If a conversion error occurs, the default converter raises Http404.  All of this is configurable and extensible (read on).


Supported Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Out of the box, DMP converts types in the following ways:

* ``str``: No conversion is necessary (a URL is already a string).
* ``int``: ``int(value)``.
* ``float``: ``float(value)``.
* ``bool``: ``value not in ('', '-', '0')``.  Anything except these three strings is True.
* Model instance id: Conversion is done by calling ``YourModel.objects.get(id=int(value))``, using the value as the id of the object.
* Any other type raises a ValueError.


Booleans
##########################

In the example above, ``forward`` has both a type hint and a default value, making it optional in the URL.  Consider how this parameter is evaluated in the following URLs:

+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30``     | Evaluates True because the third parameter is missing.  It is assigned the   |
|                                                   | default value of True (per the function signature).                          |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/``    | Evaluates False because the third parameter is present, with a value of      |
|                                                   | the empty string (the ending slash denotes the presence of this third        |
|                                                   | parameter).                                                                  |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/-/``  | Evaluates False because the third parameter is a dash `-`.  Note that a      |
|                                                   | fourth parameter is also present (after the ending slash), but it is ignored |
|                                                   | because ``process_request`` only takes three parameters.                     |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/%20/``| Evaluates True because the third parameter is a space.                       |
+---------------------------------------------------+------------------------------------------------------------------------------+

While these conversion characters may seem a little arbitrary, we assume URLs containing urlparams are created by your application code (not typed in by the user).  These characters allow you to create "pretty" urls, with a slash or zero denoting False.


Django Models
################################

URL parameters are excellent for specifying the id of model objects.  For example, suppose the id for Purchase object #1501 is coded in a receipt page URL: ``http://localhost:8000/storefront/receipt/1501/``.  The following view function signature would automatically get the object from your database:

.. code:: python

    from django_mako_plus import view_function
    from storefront.models import Purchase

    @view_function
    def process_request(request, purchase:Purchase):
        # the `purchase` variable has already been pulled from the database

In the above code, one of two outcomes will occur:

* If a Purchase record with primary key 1501 exists in the database, it is sent into the function.
* If a Purchase record with primary key 1501 does not exist in the database, DMP raises Http404.

A third outcome could also have occurred if the URL had been slightly different.  In the URL ``http://localhost:8000/storefront/receipt/-/``, the purchase object would have been ``None``, but the view function would have been called normally.  When converting Model parameters, the empty string, the dash, and a zero all cause the object to be None.  This allows your application to create URLs with objects explictily set to None.


Empty String == None
^^^^^^^^^^^^^^^^^^^^^^^

In the Python language, the empty string and None have a special relationship.  The two are separate concepts with different meanings, but both evaluate to False, acting the same in the truthy statement: ``if not mystr:``.

Denoting "empty" parameters in the url is uncertain because:

1. URLs that end with a slash, such as ``http://localhost:8000/storefront/receipt/first/second/``, essentially add an extra parameter to the urlparams list.
2. Unless told otherwise, many web servers compact double slashes into single slashes. ``http://localhost:8000/storefront/receipt//second/`` becomes ``http://localhost:8000/storefront/receipt/second/``, preventing you from ever seeing the empty first paramter.
3. There is no real concept of "None" in a URL, only an empty string or some character *denoting* a None.

Because of these difficulties, the urlparams list is programmed to never return None and never raise IndexError.  Even in a short URL with only a few parameters, accessing ``request.urlparams[50]`` returns an empty string.

For this reason, the default converters for booleans and Models objects equate the empty string *and* dash '-' as the token for False and None, respectively.  The single dash is especially useful because it provides a character in the URL (so your web server doesn't compact that position) and explicitly states the value.  Your custom converters can override this behavior, but be sure to check for the empty string in ``request.urlparams`` instead of ``None``.



Extending the Default Converter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The built-in DMP converter is built to be extended.  When you need to add a new type, simply plug a new method into the converter.  Let's add the ``timedelta`` type to the default converter.

Add the following to the end of ``homepage/__init__.py``.  The ``__init__.py`` file of one of your apps is a reliable location for this code, but you can actually put it in any module of your project that loads at Django startup.

.. code:: python

    from django_mako_plus import set_default_converter, DefaultConverter
    from datetime import datetime, timedelta
    import re

    class CustomConverter(DefaultConverter):

        @DefaultConverter.convert_method(timedelta)
        def convert_timedelta(self, value, parameter, task):
            if value not in ('', '-'):
                match = re.search('(\d+):(\d+)', value)
                if match is not None:
                    return timedelta(hours=int(match.group(1)), minutes=int(match.group(2)))
            return timedelta(hours=0)

    # set as the default for all view functions
    set_default_converter(CustomConverter)

Then change your view function code to the following:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime, timedelta
    from .. import dmp_render, dmp_render_to_string

    @view_function
    def process_request(request, delta:timedelta='0:00', forward:bool=True):
        if forward:
            now = datetime.now() + delta
        else:
            now = datetime.now() - delta
        context = {
            'now': now,
        }
        return dmp_render(request, 'index.html', context)

Conversion methods are linked to types with the ``@DefaultConverter.convert_method`` decorator.  At system startup, the class registers these types and methods, sorted by type specificity.  On each request, the converter object searches its registered methods based on the type hints.  It calls ``isinstance`` to find the right converter, which enables it to match both exact types and inherited types.


Writing Custom Converters
------------------------------

Extending the default converter (as described above) is the suggested way to convert custom types, but converters are really just callables.  If the default converter class doesn't work for you, or if one of your view functions needs special conversion, you can set the converter callable directly in the ``@view_function`` decorator.


Conversion Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Conversion functions have the following signature:

``def convert(value, parameter, task):``

* ``value`` - The value from the urlparams.  This is always a string, even if the empty string (never None).
* ``parameter`` - An object containing the name, poosition, type hint, default value, and other information about the parameter.
* ``task`` - An object containing meta-information about the current conversion task, including the request object, the ``@view_function`` decorator kwargs, the view function module, view function reference, and converter function being run.

In most cases, ``value`` and ``parameter.type`` are all you need to use in your conversion function.

Let's specify a custom converter for the view function to convert the function call parameters:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function, view_parameter
    from datetime import datetime, timedelta
    from .. import dmp_render, dmp_render_to_string
    import re

    def convert(value, parameter, task):
        if isinstance(value, parameter.type):  # already the right type (from a default)?
            return value
        elif parameter.type is timedelta:      # converting to a timedelta?
            if value not in ('', '-'):
                match = re.search('(\d+):(\d+)', value)
                if match is not None:
                    return timedelta(hours=int(match.group(1)), minutes=int(match.group(2)))
            return None
        elif parameter.type is bool:           # converting to a bool?
            return value == '+'
        return value

    @view_function(converter=convert)
    def process_request(request, delta:timedelta='0:00', forward:bool=True):
        if forward:
            now = datetime.now() + delta
        else:
            now = datetime.now() - delta
        context = {
            'now': now,
        }
        return dmp_render(request, 'index.html', context)

In this case, the converter is called twice: once for ``delta`` and once for ``forward``.  This will happen *even if the URL is too short*.  Consider how the following URLs would be handled:

+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6:30/T/``  | | ``convert('6:30', ...)`` is called for the ``delta`` parameter.            |
|                                                   | | ``convert('T', ...)`` is called for the ``forward`` parameter.             |
|                                                   | | The third urlparam (specified in the url after the last slash) is ignored. |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6:30/``    | | ``convert('6:30', ...)`` is called for the ``delta`` parameter.            |
|                                                   | | ``convert('', ...)`` is called for the ``forward`` parameter               |
|                                                   |    (specified in the url after the last slash).                              |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/00:00``    | | ``convert('00:00', ...)`` is called for the ``delta`` parameter.           |
|                                                   | | ``convert(True, ...)`` is called for the ``forward`` parameter             |
|                                                   |    (using the default in the function signature).                            |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/``         | | ``convert('', ...)`` is called for the ``delta`` parameter                 |
|                                                   |    (specified in the url after the last slash).                              |
|                                                   | | ``convert(True, ...)`` is called for the ``forward`` parameter             |
|                                                   |    (using the default in the function signature).                            |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index``          | | ``convert('0:00', ...)`` is called for the ``delta`` parameter             |
|                                                   |    (using the default in the function signature).                            |
|                                                   | | ``convert(True, ...)`` is called for the ``forward`` parameter             |
|                                                   |    (using the default in the function signature).                            |
+---------------------------------------------------+------------------------------------------------------------------------------+


Writing Parameter Converters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When only some parameters need conversion, specify converters at the parameter level instead of the function level.

Let's simplify the code to convert the ``delta`` parameter.  The boolean parameter can be handled by the DMP default converter.

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function, view_parameter
    from datetime import datetime, timedelta
    from .. import dmp_render, dmp_render_to_string
    import re

    def convert_delta(value, parameter, task):
        if value not in ('', '-'):
            match = re.search('(\d+):(\d+)', value)
            if match is not None:
                return timedelta(hours=int(match.group(1)), minutes=int(match.group(2)))
        return timedelta(hours=0)

    @view_function
    @view_parameter('delta', converter=convert_delta)
    def process_request(request, delta, forward:bool=True):
        if forward:
            now = datetime.now() + delta
        else:
            now = datetime.now() - delta
        context = {
            'now': now,
        }
        return dmp_render(request, 'index.html', context)

Our new function uses the ``custom_delta`` converter for the first parameter, but allows the default DMP converter to handle the boolean.

In addition to the converter, you can specify the type and default in the decorator.  The following arguments are valid in the ``@view_parameter`` decorator:

* ``name`` (required) - The parameter name in the signature this decorator is for.
* ``type`` - The type of the parameter.  This overrides any type hint given in the function signature.
* ``default`` - The default value for the parameter.  This overrides any default given in the function signature.
* ``converter`` - A function, lambda, or other callable that takes the three parameters described in the previous section.  This function is called to convert the value from the urlparams.


Throroughly Confused?
------------------------

The point of this tutorial has been, "How do I get values from the URL into my view function?"  DMP gives a number of ways to automate this task, and once converters are set up right, it creates clean and straightforward view function signatures.

However, the number of approaches can be daunting at first.  The following table gives advice on which approach to take:

+----------------------------------------------+----------------------------------------------------------------------------------------+
| If your view function needs:                 | Then use this approach:                                                                |
+==============================================+========================================================================================+
| String values from the URL                   | `Add new parameters to your view function <Approach 2: The Automated Way_>`_.          |
|                                              | No type hints or defaults are needed for strings.                                      |
+----------------------------------------------+----------------------------------------------------------------------------------------+
| Integer, float, or boolean values,           | `Add type hints in your function signature <Adding Type Hints_>`_.                     |
| or Model object ids from the URL             | DMP will convert the URL values automatically.                                         |
+----------------------------------------------+----------------------------------------------------------------------------------------+
| Values of other types from the URL           | `Extend the django_mako_plus.DefaultConverter class                                    |
|                                              | <Extending the Default Converter_>`_, and set it as the default converter.             |
+----------------------------------------------+----------------------------------------------------------------------------------------+
| A custom conversion process for a single     | `Create a custom converter function <Conversion Functions_>`_,                         |
| function                                     | and specify it in the ``@view_function`` decorator.                                    |
+----------------------------------------------+----------------------------------------------------------------------------------------+
| A specific type of parameter conversion      | `Create a parameter converter function <Writing Parameter Converters_>`_,              |
|                                              | and connect it to the correct parameter using the                                      |
|                                              | ``@view_parameter`` decorator.                                                         |
+----------------------------------------------+----------------------------------------------------------------------------------------+
| Directly access the URL parts.               | Simply `use the request.urlparams list <Approach 1: request.urlparams_>`_ directly.    |
+----------------------------------------------+----------------------------------------------------------------------------------------+
