Customizing @view_function
--------------------------------------

.. contents::
    :depth: 2


The ``@view_function`` decorator is responsible for two things:

1. Denoting which functions in your project are web-accessible.
2. Converting url parameters just before calling your functions.

As a decorator for all endpoints in your system, it is a great place to fully customize parameter conversion or perform other pre-endpoint work.  ``@view_function`` is programmed as a class-based decorator so it can be extended!

Customizing Parameter Conversion
======================================

The standard method of parameter conversion, `adding a conversion function </topics_converters.html#adding-a-new-converter>`_, should work for most situations.  However, extending ``@view_function`` gives control over the entire conversion process.

In the ``convert_parameters()`` method (called per request), the decorator iterates the parameters in your view function signature and calls ``convert_value`` for each one.  Within ``convert_value``, it determines the appropriate converter function for the given parameter.

Suppose you need to convert the first url parameter in a standard way, regardless of its type.  The following code checks the parameter by position in the view function signature:

.. code:: python

    from django_mako_plus import view_parameter

    class site_endpoint(view_function):
        '''Customized view function decorator'''

        def convert_value(self, value, parameter, request):
            # in the view function signature, request is position 0
            # and the first url parameter is position 1
            if parameter.position == 1:
                return some_custom_converter(value, parameter)

            # any other url params convert the normal way
            return super().convert_value(value, parameter, request)

Then in ``homepage/views/index.py``, use your custom decorator:

.. code:: python

    from .some.where import site_endpoint

    @site_endpoint
    def process_request(request, param1, param2, param3):
        ...

The above code customizes the conversion of individual parameters.  To customize the entire conversion process, override the ``convert_parameters`` method.


Using Keyword Arguments
=============================

Although we normally specify ``@view_function`` without any arguments, it can take an arbitrary number of keyword arguments.  Any extra arguments are placed in the ``self.options`` dictionary.

    In the code below, I don't really need to override ``__init__.py`` because the super makes ``.options``.  However, I'm creating ``__init__`` just for code readability.

For this example, lets check user groups in the view function decorator.

    Yeah, I know this example isn't the best.  We really should use permission-based security rather than group-based security.  And Django already comes with the ``@require_permission`` decorator.  The point is to show how to use keyword arguments with a customized view function decorator.  Let's try to focus on that. :)

Override the ``__call__`` method, which runs just before your endpoint:

.. code:: python

    from django_mako_plus import view_parameter

    class site_endpoint(view_function):
        '''Customized view unction decorator'''

        def __init__(self, f, require_role=None, **options):
            super().__init__(self, f, **options)
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
