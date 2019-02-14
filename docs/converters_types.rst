Supported Types
================================

.. contents::
    :depth: 2


The following view function signature expects two additional parameters in the url: ``hrs`` and ``mins``.  DMP converts these to ``int`` automatically.

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

Built-in Types
-------------------------------

Out of the box, DMP converts the following types:

+---------------------------+--------------------------------------------------------------+---------------------------------------------------+
| Type Hint:                | Conversion:                                                  | Empty (default used) when value is:               |
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


Boolean Values
----------------------

Consider the following signature:

.. code-block:: python

    @view_function
    def process_request(request, forward:bool=True):
        ...

In the signature, ``forward`` has a type hint *and* a default value, making it optional in the URL.  Consider how ``forward`` is evaluated in the following URLs:

+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30``     | Evaluates True because the third parameter is missing.  It is assigned the   |
|                                                   | default value of True (per the function signature).                          |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/0/``  | Evaluates False because the third parameter is ``0``.                        |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/0/``  | Evaluates False because the third parameter is ``f``.                        |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/AA/`` | Evaluates True because the third parameter is ``AA``                         |
|                                                   | (not one of the False characters).                                           |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/-/``  | Evaluates True because the third parameter is a dash ``-``, and DMP assigns  |
|                                                   | the parameter default (``forward:bool=True``).                               |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6/30/%20/``| Evaluates True because the third parameter is a space, and DMP assigns       |
|                                                   | the parameter default (``forward:bool=True``).                               |
+---------------------------------------------------+------------------------------------------------------------------------------+

While these conversion characters may seem a little arbitrary, these characters allow you to create "pretty" urls, with a dash denoting "empty".


Django Models
---------------------------

URL parameters are excellent places to specify ids of model objects.  For example, suppose the id for Purchase object #1501 is coded in a receipt page URL: ``http://localhost:8000/storefront/receipt/1501/``.  The following view function signature would automatically get the object from your database:

.. code-block:: python

    from django_mako_plus import view_function
    from storefront.models import Purchase

    @view_function
    def process_request(request, purchase:Purchase):
        # the `purchase` variable has already been pulled from the database

In the above URL, one of two outcomes will occur:

* If a Purchase record with primary key 1501 exists in the database, it is sent into the function.
* If it doesn't exist, DMP raises Http404.

But in the slightly different URL, ``http://localhost:8000/storefront/receipt/-/``, a third option happens. The view function *is called*, even though "dash" isn't a valid object ID.  Since the dash means "empty", the ``purchase`` parameter will be ``None``. In fact, when converting Model parameters, the empty string, the dash, and a zero all cause the object to be None.

The purpose of the "empty" values, which calls the function with ``purchase => None``, allows your application to create URLs with objects explictily set to None.


Specifying Model Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since Python usually parses converter functions **before** your models are ready, you can't reference them by type.  This issue is `described in the Django documentation <https://docs.djangoproject.com/en/dev/ref/models/fields/#module-django.db.models.fields.related>`_.

In other words, the following doesn't work:

.. code-block:: python

    from django_mako_plus import parameter_converter
    from homepage.models import Question

    @parameter_converter(Question)
    def convert_question(value, parameter):
        ...


DMP uses the same solution as Django when referencing models: use "app.Model" syntax.  In the following function, we specify the type as a string.  After Django starts up, DMP replaces the string with the actual type.

.. code-block:: python

    from django_mako_plus import parameter_converter

    @parameter_converter("homepage.Question")
    def convert_question(value, parameter):
        ...

Using string-based types only works with models (not with other types).
