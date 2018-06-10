Parameter Conversion
==========================

.. contents::
    :depth: 2

DMP automatically converts URL parameters for you.  To enable this, simply put standard Python type hints in your ``process_request`` functions:

.. code:: python

    def process_request(request, name:str, age:int=40, happy:bool=True):
        ...

These were already discussed in other areas of our documentation:

    * `Built-in Converters </tutorial_urlparams.html#automatic-type-converters>`_ for a list of supported types.
    * `Converting URL Parameters </basics_converters.html>`_ for the primer.

This page contains more advanced conversion topics.



Raw Parameter Values
-------------------------

During URL resolution, DMP populates the ``request.dmp.urlparams[ ]`` list with all URL parts *after* the first two parts (``/homepage/index/``), up to the ``?`` (query string).  For example, the URL ``/homepage/index/144/A58UX/`` has two urlparams: ``144`` and ``A58UX``.  These can be accessed as ``request.dmp.urlparams[0]`` and ``request.dmp.urlparams[1]`` throughout your view function.

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



Conversion Errors
--------------------------------

Suppose we use a url of ``/homepage/index/Homer/a/t/`` to the example above.  The integer converter will fail because ``a`` is not a valid integer.  A ValueError is raised.

When this occurs, the default behavior of DMP is to raise an Http404 exception, indicating to the browser that the given url does not exist.

If you want a different resolution to conversion errors, such as a redirect, the sections below explain how to customize the conversion process.



Adding a Custom Converter
--------------------------------


Suppose we want to use geographic locations in the format "20.4,-162.0".  The URL might looks something like this:

``http://localhost:8000/homepage/index/20.4,-162.0/``


Let's place our new class and converter function in ``homepage/__init__.py`` (you can actually place these in any file that loads with Django). Decorate the function with ``@parameter_converter``, with the type(s) as arguments.

.. code:: python

    from django_mako_plus import parameter_converter

    class GeoLocation(object):
        def __init__(self, latitude, longitude):
            self.latitude = latitude
            self.longitude = longitude

    @parameter_converter(GeoLocation)
    def convert_geo_location(value, parameter):
        parts = value.split(',')
        if len(parts) < 2:
            raise ValueError('Both latitude and longitude are required')
        # the float constructor will raise ValueError if invalid
        return GeoLocation(float(parts[0]), float(parts[1]))

When called, your function must do one of the following:

1. Return the converted type.
2. Raise an exception, such as:

    * a ValueError, which causes DMP to return not found (Http404) to the browser.
    * Raise DMP's RedirectException, which redirects the browser url.
    * Raise DMP's InternalRedirectException, which immediately calls a different view function (without changing the browser url).
    * Raise Django's Http404 with a custom message.

Now in ``homepage/views/index.py``, use our custom ``GeoLocation`` class as the type hint in the index file.

.. code:: python

    @view_function
    def process_request(request, loc:GeoLocation):
        print(loc.latitude)
        print(loc.longitude)
        return request.dmp.render('index.html', {})

When a request occurs, DMP will read the signature on ``process_request``, look up the ``GeoLocation`` type, and use your function to convert the string to a GeoLocation object.


Special Considerations for Models
--------------------------------------

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


Replacing the Converter
--------------------------------

There may be situations where you need to specialize the converter.  This is done by subclassing the ``ParameterConverter`` class and referencing your subclass in ``settings.py``.

As an example, suppose you need to convert the first url parameter in a standard way, regardless of its type.  The following code looks for this parameter by position:

.. code:: python

    from django_mako_plus.converter.base import ParameterConverter

    class SiteConverter(BaseConverter):
        '''Customized converter that always converts the first parameter in a standard way, regardless of type'''
        def convert_value(self, value, parameter, request):
            # in the view function signature, request is position 0
            # and the first url parameter is position 1
            if parameter.position == 1:
                return some_custom_converter(value, parameter)

            # any other url params convert the normal way
            return super().convert_value(value, parameter, request)


We'll assume you placed the class in ``myproject/lib/converters.py``.  Activate your new converter in DMP's section of ``settings.py``:

.. code:: python

    DEFAULT_OPTIONS = {
        'PARAMETER_CONVERTER': 'lib.converters.SiteConverter',
    }

All parameters in the system will now use your customization rather than the standard DMP converter.



Non-Wrapping Decorators
--------------------------------

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

If the developer of ``@other_decorator`` didn't "wrap" it correctly, DMP will **read the signature from the wrong function**: ``def other_decorator(...)`` instead of ``def process_request(...)``!  This issue is well known in the Python community -- Google "fix your python decorators" to read many blog posts about it.

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


Disabling the Converter
------------------------------

If you want to entirely disable the parameter converter, set DMP's converter setting to None.  This will result in a slight speedup.

.. code:: python

    DEFAULT_OPTIONS = {
        'PARAMETER_CONVERTER': None,
    }
