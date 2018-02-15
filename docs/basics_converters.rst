Converting URL Parameters
--------------------------------------

.. contents::
    :depth: 2


In the `initial tutorial <tutorial_urlparams.html>`_, you learned that any extra parameters in the URL are sent to your view function as parameters.  For example the following view function signature expects two additional parameters in the url: ``hrs`` and ``mins``.  DMP converts these to ``int`` automatically.

.. code:: python

    @view_function
    def process_request(request, hrs:int=12, mins:int=30):
        ...

In the above function, ``hrs`` and ``mins`` are set to the following integers:

+--------------------------------------------------+-----------------------------------------------------------------------+
| ``/homepage/index/111/222/``                     | ``hrs=111``; ``mins=222``                                             |
+--------------------------------------------------+-----------------------------------------------------------------------+
| ``/homepage/index/111/222``                      | ``hrs=111``; ``mins=222``                                             |
+--------------------------------------------------+-----------------------------------------------------------------------+
| ``/homepage/index/-/222``                        | ``hrs=12`` (default); ``mins=222``                                    |
+--------------------------------------------------+-----------------------------------------------------------------------+
| ``/homepage/index//222``                         | ``hrs=12`` (default); ``mins=222``                                    |
+--------------------------------------------------+-----------------------------------------------------------------------+
| ``/homepage/index/111``                          | ``hrs=111``; ``mins=30`` (default)                                    |
+--------------------------------------------------+-----------------------------------------------------------------------+

Supported Types
^^^^^^^^^^^^^^^^^^^^^

Out of the box, DMP converts the following types:

+---------------------------+-------------------------------------------------------------+---------------------------------------------------+
| Type Hint:                | Conversion:                                                 | Use parameter default when value is:              |
+===========================+=============================================================+===================================================+
| ``str``                   | No conversion                                               | ``''``                                            |
+---------------------------+-------------------------------------------------------------+---------------------------------------------------+
| ``int``                   | ``int(value)``                                              | ``''``, ``-``                                     |
+---------------------------+-------------------------------------------------------------+---------------------------------------------------+
| ``float`                  | ``float(value)``                                            | ``''``, ``-``                                     |
+---------------------------+-------------------------------------------------------------+---------------------------------------------------+
| ``decimal.Decimal``       | ``decimal.Decimal(value)``                                  | ``''``, ``-``                                     |
+---------------------------+-------------------------------------------------------------+---------------------------------------------------+
| ``bool``                  | ``value[0] not in ( 'f', 'F', '0', False )``                | ``''``, ``-`` (see notes below)                   |
+---------------------------+-------------------------------------------------------------+---------------------------------------------------+
| ``datetime.datetime``     | First matching format in ``settings.DATETIME_INPUT_FORMATS` | ``''``, ``-``                                     |
+---------------------------+-------------------------------------------------------------+---------------------------------------------------+
| ``datetime.date``         | First matching format in ``settings.DATE_INPUT_FORMATS``    | ``''``, ``-``                                     |
+---------------------------+-------------------------------------------------------------+---------------------------------------------------+
| ``Model`` subclass        | ``YourModel.objects.get(id=value)``                         | ``''``, ``-``, ``0`` (see notes below)            |
+---------------------------+-------------------------------------------------------------+---------------------------------------------------+
| ``object``                | The fallback, no conversion                                 | ``''``                                            |
+---------------------------+-------------------------------------------------------------+---------------------------------------------------+

Notes about bool:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the example above, ``forward`` has a type hint *and* a default value, making it optional in the URL.  Consider how ``forward`` is evaluated in the following URLs:

+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30``     | Evaluates True because the third parameter is missing.  It is assigned the   |
|                                                   | default value of True (per the function signature).                          |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/0/``  | Evaluates False because the third parameter is ``0``.                        |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/0/``  | Evaluates False because the third parameter is ``f``.                        |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/AA/`` | Evaluates True because the third parameter is ``AA``                         |
|                                                   | (one of the False characters).                                               |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/-/``  | Evaluates True because the third parameter is a dash ``-``, and DMP assigns  |
|                                                   | the parameter default (``forward:bool=True``).                               |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/%20/``| Evaluates True because the third parameter is a space                        |
|                                                   | (one of the False characters).                                               |
+---------------------------------------------------+------------------------------------------------------------------------------+

While these conversion characters may seem a little arbitrary, these characters allow you to create "pretty" urls, with a dash or zero denoting False.

Notes about Django Models:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Non-Wrapping Decorators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Automatic conversion is done using ``inspect.signature``, which comes standard with Python.  This function reads your ``process_request`` source code signature and gives DMP the parameter hints.  As we saw in the `tutorial <tutorial_urlparams.html#adding-type-hints>`_, your code specifies these hints with something like the following:

.. code:: python

    @view_function
    def process_request(request, hrs:int, mins:int, forward:bool=True):
        ...

The trigger for DMP to read parameter hints is the ``@view_function`` decorator, which signals a callable endpoint to DMP.  When it sees this decorator, DMP goes to the wrapped function, ``process_request``, and inspects the hints.

Normally, this process works without issues.  But it can fail when certain decorators are chained together.  Consider the following code:

.. code:: python

    @view_function
    @other_decorator   # this might mess up the type hints!
    def process_request(request, hrs:int, mins:int, forward:bool=True):
        ...

If the developer of ``@other_decorator`` didn't "wrap" it correctly, DMP will **read the signature from the wrong function**: ``def other_decorator(...)`` instead of ``def process_request(...)``!

Debugging when this occurs can be fubar and hazardous to your health.  Unwrapped decorators are essentially just function calls, and there is no way for DMP to differentiate them from your endpoints (without using hacks like reading your source code). You'll know something is wrong because DMP will ignore your parameters, sent them the wrong values, or throw unexpected exceptions during conversion.  If you are using multiple decorators on your endpoints, check the wrapping before you debug too much (next paragraph).

You can avoid/fix this issue by ensuring each decorator you are using is wrapped correctly, per the Python decorator pattern.  When coding ``other_decorator``, be sure to include the ``@wraps(func)`` line.  You can read more about this in the `Standard Python Documentation <https://docs.python.org/3/library/functools.html#functools.wraps>`_.  The pattern looks something like the following:

.. code:: python

    from functools import wraps

    def other_decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # decorator work here goes here
            # ...
            # call the endpoint
            return func(request, *args, **kwargs)
        # outer function return
        return wrapper

When your inner function is decorated with ``@wraps``, DMP is able to "unwrap" the decorator chain to the real endpoint function.

    If your decorator comes from third-party code that you can't control, one solution is to create a new decorator (following the pattern above) that calls the third-party function as its "work". Then decorate functions with your own decorator rather than the third-party decorator.

Raw Parameter Values
^^^^^^^^^^^^^^^^^^^^^^^^

In its view middleware, DMP populates the ``request.dmp.urlparams[ ]`` list with all URL parts *after* the first two parts (``/homepage/index/``), up to the ``?`` (query string).  For example, the URL ``/homepage/index/144/A58UX/`` has two urlparams: ``144`` and ``A58UX``.  These can be accessed as ``request.dmp.urlparams[0]`` and ``request.dmp.urlparams[1]`` throughout your view function.

Empty parameters and trailing slashes are handled in a specific way.  The following table gives examples:

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

In the Python language, the empty string and None have a special relationship.  The two are separate concepts with different meanings, but both evaluate to False, acting the same in the truthy statement: ``if not mystr:``.

Denoting "empty" parameters in the url is uncertain because:

1. Unless told otherwise, many web servers compact double slashes into single slashes. ``http://localhost:8000/storefront/receipt//second/`` becomes ``http://localhost:8000/storefront/receipt/second/``, preventing you from ever seeing the empty first paramter.
2. There is no real concept of "None" in a URL, only an empty string or some character *denoting* the absence of value.

Because of these difficulties, the urlparams list is programmed to never return None and never raise IndexError.  Even in a short URL with only a few parameters, accessing ``request.dmp.urlparams[50]`` returns an empty string.

For this reason, the default converters for booleans and Models objects equate the empty string *and* dash '-' as the token for False and None, respectively.  The single dash is especially useful because it provides a character in the URL (so your web server doesn't compact that position) and explicitly states the value.  Your custom converters can override this behavior, but be sure to check for the empty string in ``request.dmp.urlparams`` instead of ``None``.

