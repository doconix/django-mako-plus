Customizing the Converter
===================================

There may be situations where you need to specialize or even replace the converter.  This is done by subclassing the ``ParameterConverter`` class and referencing your subclass in ``settings.py``.

    Note that we already discussed creating a custom converter class to `handle converter errors <converters_errors.html>`_.

Suppose you need to convert the first url parameter in a standard way, regardless of its type.  The following code looks for this parameter by position:

.. code-block:: python

    from django_mako_plus import ParameterConverter

    class SiteConverter(ParameterConverter):
        '''Customized converter that always converts the first parameter in a standard way, regardless of type'''

        def convert_value(self, value, parameter, request):
            # in the view function signature, request is position 0
            # and the first url parameter is position 1
            if parameter.position == 1:
                return some_custom_converter(value, parameter, request)

            # any other url params convert the normal way
            return super().convert_value(value, parameter, request)


We'll assume you placed the class in ``myproject/lib/converters.py``.  Activate your new converter in DMP's section of ``settings.py``:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'PARAMETER_CONVERTER': 'lib.converters.SiteConverter',
                ...
            }
        }
    ]

All parameters in the system will now use your customization rather than the standard DMP converter.




Disabling the Converter
------------------------------

If you want to entirely disable parameter conversion, set DMP's converter setting to None in ``settings.py``.  This will result in a slight processing speedup.

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'PARAMETER_CONVERTER': None,
                ...
            }
        }
    ]
