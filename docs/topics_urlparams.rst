Custom Parameter Converters
--------------------------------------

In the tutorial, I showed how to add type hints for automatic parameter conversion.  This toipc shows how to convert additional types.

.. contents::
    :depth: 2


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




Replacing the Default Converter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the default converter class doesn't work for you, or if one of your view functions needs special conversion, set a custom function in the ``@view_function`` decorator.  Converters can be any callable, including functions, lambdas, or classes that define ``__call__``.

Conversion functions have the following signature and parameters:

``def convert(value, parameter, task):``

* ``value`` - The value from the urlparams.  This is always a string, even if the empty string (never None).
* ``parameter`` - An object containing the name, poosition, type hint, default value, and other information about the parameter.
* ``task`` - An object containing meta-information about the current conversion task, including the request object, the view function module, view function reference, and converter function being run.

In most cases, ``value`` and ``parameter.type`` are all you need to make a converter function.  Let's create a basic function to handle our types:

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
|                                                   |    (the last slash creates the empty string value).                          |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/00:00``    | | ``convert('00:00', ...)`` is called for the ``delta`` parameter.           |
|                                                   | | ``convert(True, ...)`` is called for the ``forward`` parameter             |
|                                                   |    (using the default in the function signature).                            |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/``         | | ``convert('', ...)`` is called for the ``delta`` parameter                 |
|                                                   |    (the last slash creates the empty string value).                          |
|                                                   | | ``convert(True, ...)`` is called for the ``forward`` parameter             |
|                                                   |    (using the default in the function signature).                            |
+---------------------------------------------------+------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index``          | | ``convert('0:00', ...)`` is called for the ``delta`` parameter             |
|                                                   |    (using the default in the function signature).                            |
|                                                   | | ``convert(True, ...)`` is called for the ``forward`` parameter             |
|                                                   |    (using the default in the function signature).                            |
+---------------------------------------------------+------------------------------------------------------------------------------+

