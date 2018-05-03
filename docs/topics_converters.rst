Parameter Conversion
--------------------------------------

.. contents::
    :depth: 2

DMP automatically converts URL parameters for you.  To enable this, simply put standard Python type hints in your ``process_request`` functions:

.. code:: python

    def process_request(request, name:str, age:int=40, happy:bool=True):
        ...

See the `built-in converter table </tutorial_urlparams.html#automatic-type-converters>`_ for details on the supported types.


Empty Values
=========================

Python's ``None`` doesn't really exist in URLs.  For example, in the url ``/homepage/index//``, the first url parameter is the empty string.  Without the concept of ``None``, how do we decide when to use the default value, such as the value of 40 for the age above?

Since the starting value is always a string, DMP's conversion functions use a few hard-coded strings to denote the "empty" value.  For example, if the integer converter gets an empty string ``''`` or a dash ``'-'``, it uses the default value.  In the example above, the url of ``/homepage/index/Homer/-/t/`` sets ``age=40`` since the dash is considered "empty".

The `built-in converter table </tutorial_urlparams.html#automatic-type-converters>`_ lists the "empty" values for each converter type.


Conversion Errors
=========================

Suppose we use a url of ``/homepage/index/Homer/a/t/`` to the example above.  The integer converter will fail because ``a`` is not a valid integer.  A ValueError is raised.

When this occurs, the default behavior of DMP is to raise an Http404 exception, indicating to the browser that the given url does not exist.

If you want a different resolution to conversion errors, such as a redirect, the sections below explain how to customize the conversion process.


Adding a New Converter
==========================

It's easy to add new type converters to DMP.  Suppose we want to use geographic locations in the format "20.4,-162.0".  We'd first need a type and view function:

.. code:: python

    class GeoLocation(object):
        def __init__(self, latitude, longitude):
            self.latitude = latitude
            self.longitude = longitude

.. code:: python

    @view_function
    def process_request(request, loc:GeoLocation):
        print(loc.latitude)
        print(loc.longitude)


The converter should be placed in a file that loads with Django, such as ``homepage/apps.py`` or ``homepage/__init__.py``.  Decorate the function with ``@parameter_converter``, with the type(s) as arguments.

When called, your function must:

* Return the converted type.
* Raise an exception, such as:
    * a ValueError, which causes DMP to return not found (Http404) to the browser.
    * Raise DMP's RedirectException, which redirects the browser user.
    * Raise DMP's InternalRedirectException, which immediately calls a different view function (without changing the browser url).
    * Raise Django's Http404 with a custom message.

The completed function:

.. code:: python

    from django_mako_plus import parameter_converter

    @parameter_converter(GeoLocation)
    def convert_geo_location(value, parameter):
        parts = value.split(',')
        if len(parts) < 2:
            raise ValueError('Both latitude and longitude are required')
        # the float constructor will raise ValueError if invalid
        return GeoLocation(float(parts[0]), float(parts[1]))


When the request occurs, DMP will read the signature on ``process_request`` and call your conversion function.


Special Considerations for Models
========================================

Since Python usually parses converter functions **before** your models are ready, you can't reference them by type.  This issue is `described in the Django documentation <https://docs.djangoproject.com/en/dev/ref/models/fields/#module-django.db.models.fields.related>`_.

In other words, the following doesn't work:

.. code:: python

    from django_mako_plus import parameter_converter
    from homepage.models import Question

    @parameter_converter(Question)
    def convert_question(value, parameter):
        ...


DMP uses the same solution as Django when referencing models: use "app.Model" syntax.  In the following function, we specify the type as a string.  After Django starts up, DMP replaces the string with the actual type.

.. code:: python

    from django_mako_plus import parameter_converter

    @parameter_converter("homepage.Question")
    def convert_question(value, parameter):
        ...

Using string-based types only works with models (not with other types).
