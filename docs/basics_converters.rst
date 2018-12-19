Converting URL Parameters
--------------------------------------

.. contents::
    :depth: 2


In the `initial tutorial <tutorial_urlparams.html>`_, you learned that any extra parameters in the URL are sent to your view function as parameters.  For example the following view function signature expects two additional parameters in the url: ``hrs`` and ``mins``.  DMP converts these to ``int`` automatically.

.. code-block:: python

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

+---------------------------+--------------------------------------------------------------+---------------------------------------------------+
| Type Hint:                | Conversion:                                                  | Use parameter default when value is:              |
+===========================+==============================================================+===================================================+
| ``str``                   | No conversion                                                | ``''``                                            |
+---------------------------+--------------------------------------------------------------+---------------------------------------------------+
| ``int``                   | ``int(value)``                                               | ``''``, ``-``                                     |
+---------------------------+--------------------------------------------------------------+---------------------------------------------------+
| ``float``                 | ``float(value)``                                             | ``''``, ``-``                                     |
+---------------------------+--------------------------------------------------------------+---------------------------------------------------+
| ``decimal.Decimal``       | ``decimal.Decimal(value)``                                   | ``''``, ``-``                                     |
+---------------------------+--------------------------------------------------------------+---------------------------------------------------+
| ``bool``                  | ``value[0] not in ( 'f', 'F', '0', False )``                 | ``''``, ``-`` (see notes below)                   |
+---------------------------+--------------------------------------------------------------+---------------------------------------------------+
| ``datetime.datetime``     | First matching format in ``settings.DATETIME_INPUT_FORMATS`` | ``''``, ``-``                                     |
+---------------------------+--------------------------------------------------------------+---------------------------------------------------+
| ``datetime.date``         | First matching format in ``settings.DATE_INPUT_FORMATS``     | ``''``, ``-``                                     |
+---------------------------+--------------------------------------------------------------+---------------------------------------------------+
| ``Model`` subclass        | ``YourModel.objects.get(id=value)``                          | ``''``, ``-``, ``0`` (see notes below)            |
+---------------------------+--------------------------------------------------------------+---------------------------------------------------+
| ``object``                | The fallback, no conversion                                  | ``''``                                            |
+---------------------------+--------------------------------------------------------------+---------------------------------------------------+

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

.. code-block:: python

    from django_mako_plus import view_function
    from storefront.models import Purchase

    @view_function
    def process_request(request, purchase:Purchase):
        # the `purchase` variable has already been pulled from the database

In the above code, one of two outcomes will occur:

* If a Purchase record with primary key 1501 exists in the database, it is sent into the function.
* If it doesn't exist, DMP raises Http404.

A third outcome could also have occurred if the URL had been slightly different.  In the URL ``http://localhost:8000/storefront/receipt/-/``, the purchase object would be ``None``, but the view function still would be called normally.  When converting Model parameters, the empty string, the dash, and a zero all cause the object to be None.  This allows your application to create URLs with objects explictily set to None.


More Information
^^^^^^^^^^^^^^^^^^^^^

The advanced topic on `Parameter Conversion </topics_converters.html>`_ contains more information about converters, such as empty values, accessing the raw url values, conversion errors, and creating custom converter objects.
