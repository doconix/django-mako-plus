.. _converters_errors:

Errors During Conversion
===============================

When conversion fails, the default behavior of DMP is to raise an ``Http404`` exception, indicating to the browser that the given url does not exist. Most of the time, this makes sense because it is, in effect, an invalid URL.

Resolution is as follows:

* If a converter function raises ``ValueError`` on any parameter, an Http 404 response is returned to the browser, indicating that the conversion failed for "normal" reasons.
* If a converter function raises any other type of exception, a ``ConverterException`` is raised, indicating that an unexpected error occurred during conversion. This generally returns an Http 500 server error to the browser.


Customizing
---------------------------------

Enough of this 404 rudeness! Suppose we want to be more forgiving of converter failures. When converter functions raise ``ValueError``, we'll use the view function defaults and let processing continue normally.

For example, consider the following view function in ``index.py``:

.. code-block:: python

    from django_mako_plus import view_function

    @view_function
    def process_request(request, age:int=0):
        ...

With this view function:

* ``/homepage/index/5/`` works perfectly: the function is called with ``age=5``.
* ``/homepage/index/asdf/`` fails the conversion to integer: the Http 404 page is returned.

Let's extend the ``ParameterConverter`` class to catch the 404 and return the default. Add the following to ``/homepage/apps.py``:

.. code-block:: python

    from django.apps import AppConfig
    from django.http import Http404
    from django_mako_plus import ParameterConverter
    import inspect

    class HomepageConfig(AppConfig):
        name = 'homepage'


    class ForgivingConverter(ParameterConverter):
        '''Uses defaults for values that cannot be converted (instead of the usual 404)'''

        def convert_value(self, value, parameter, request):
            try:                                # try the normal conversion process
                return super().convert_value(value, parameter, request)

            except Http404:                     # converter function raised a ValueError
                if parameter.default is not inspect.Parameter.empty:
                    return parameter.default    # return the default specified in process_request() signature
                return None                     # return None if signature has no default

Activate the custom converter in ``settings.py``:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'PARAMETER_CONVERTER': 'homepage.apps.ForgivingConverter',
                ...
            }
        }
    ]

With the above setup, converter failures will no longer trigger a 404. Instead, the default value is used anytime a conversion fails.
