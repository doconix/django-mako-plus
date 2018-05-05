Customizing @view_function
--------------------------------------

.. contents::
    :depth: 2


The ``@view_function`` decorator is responsible for two things:

1. Denoting which functions in your project are web-accessible.
2. Converting url parameters just before calling your functions.

As a decorator for all endpoints in your system, it is a great place to fully customize parameter conversion or perform other pre-endpoint work.  ``@view_function`` was intentionally programmed as a class-based decorator so you can extend it.


Using Keyword Arguments
=============================

Although we normally specify ``@view_function`` without any arguments, it can take an arbitrary number of keyword arguments.  Any extra arguments are placed in the ``self.options`` dictionary.

For this example, lets check user groups in the view function decorator.  We really should use permission-based security rather than group-based security.  And Django already comes with the ``@require_permission`` decorator.  So perhaps this is a bit of a contrived example.  But let's go with it.

Override the ``__call__`` method, which runs just before your endpoint:

.. code:: python

    from django_mako_plus import view_parameter

    class site_endpoint(view_function):
        '''Customized view function decorator'''

        def __init__(self, f, require_role=None, *args, **kwargs):
            super().__init__(self, f, *args, **kwargs)
            self.require_role = require_role

        def __call__(self, request, *args, **kwargs):
            # check roles
            if self.require_role:
                if request.user.is_anonymous or request.user.groups.filter(name=self.require_role).count() == 0:
                    return HttpResponseRedirect('/login/')

            # call the super
            return super().__call__(request, *args, **kwargs)

In ``homepage/views/index.py``, use your custom decorator.

.. code:: python

    from .some.where import site_endpoint

    @site_endpoint(require_role='mentors')
    def process_request(request):
        ...

In the above example, overriding ``__init__`` isn't technically necessary.  Any extra ``*args`` and ``**kwargs`` in the constructor call are placed in ``self.decorator_args`` and ``self.decorator_kwargs``.  So instead of explictily listing ``require_role`` in the argument list, we could have used ``self.decorator_kwargs.get('require_role')``.  I only listed the parameter explicitly for code clarity.



Replacing the Converter
====================================

The standard method of parameter conversion, `adding a conversion function </topics_converters.html#adding-a-new-converter>`_, should work for most situations.  However, we can customize or fully replace the parameter converter if needed.

In the ``convert_parameters()`` method (called per request), the decorator iterates the parameters in your view function signature and calls ``convert_value`` for each one.  Within ``convert_value``, it determines the appropriate converter function for the given parameter.

Suppose you need to convert the first url parameter in a standard way, regardless of its type.  The following code checks the parameter by position in the view function signature:

.. code:: python

    from django_mako_plus import view_parameter
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

    class site_endpoint(view_function):
        '''Customizing the converter'''
        converter_class = SiteConverter


Then in ``homepage/views/index.py``, use your custom decorator:

.. code:: python

    from .some.where import site_endpoint

    @site_endpoint
    def process_request(request, param1, param2, param3):
        ...



Disabling the Converter
====================================

If you want to entirely disable the parameter converter, set the ``converter_class`` to None.  This will result in a slight speedup.

.. code:: python

    from django_mako_plus import view_parameter

    class site_endpoint(view_function):
        '''Disables the converter'''
        converter_class = None
