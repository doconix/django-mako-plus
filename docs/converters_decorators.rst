Non-Wrapping Decorators
=================================

    This page is important only when you use additional decorators on your view functions.

Automatic conversion is done using ``inspect.signature``, which comes standard with Python.  This function reads your ``process_request`` source code signature and gives DMP the parameter hints.  As we saw in the `tutorial <tutorial_urlparams.html#adding-type-hints>`_, your code specifies these hints with something like the following:

.. code-block:: python

    @view_function
    def process_request(request, hrs:int, mins:int, forward:bool=True):
        ...

The trigger for DMP to read parameter hints is the ``@view_function`` decorator, which signals a callable endpoint to DMP.  When it sees this decorator, DMP goes to the wrapped function, ``process_request``, and inspects the hints.

Normally, this process works without issues.  But it can fail when certain decorators are chained together.  Consider the following code:

.. code-block:: python

    @view_function
    @other_decorator   # this might mess up the type hints!
    def process_request(request, hrs:int, mins:int, forward:bool=True):
        ...

If the developer of ``@other_decorator`` didn't "wrap" it correctly, DMP will **read the signature from the wrong function**: ``def other_decorator(...)`` instead of ``def process_request(...)``!  This issue is well known in the Python community -- Google "fix your python decorators" to read many blog posts about it.

Debugging when this occurs can be fubar and hazardous to your health.  Unwrapped decorators are essentially just function calls, and there is no way for DMP to differentiate them from your endpoints (without using hacks like reading your source code). You'll know something is wrong because DMP will ignore your parameters, sent them the wrong values, or throw unexpected exceptions during conversion.  If you are using multiple decorators on your endpoints, check the wrapping before you debug too much (next paragraph).

You can avoid/fix this issue by ensuring each decorator you are using is wrapped correctly, per the Python decorator pattern.  When coding ``other_decorator``, be sure to include the ``@wraps(func)`` line.  You can read more about this in the `Standard Python Documentation <https://docs.python.org/3/library/functools.html#functools.wraps>`_.  The pattern looks something like the following:

.. code-block:: python

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
