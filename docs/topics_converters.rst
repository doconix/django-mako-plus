Custom Converters
--------------------------------------

.. contents::
    :depth: 2


Non-Wrapping Decorators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

If the developer of ``@other_decorator`` didn't "wrap" it correctly, DMP will **read the signature from the wrong function**: ``def other_decorator(...)`` instead of ``def process_request(...)``!

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


Extending the Default Converter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The built-in DMP converter is built to be extended.  When you need to add a new type, simply plug a new method into the converter.  

Conversion methods are linked to types with the ``@DefaultConverter.convert_method`` decorator.  At system startup, the class registers these types and methods, sorted by type specificity.  On each request, the converter object searches its registered methods based on the type hints.

    The converter uses ``isinstance`` to find the right converter, so it matches both exact types and inherited types.  This is how the automatic model converter is done: the single converter method for ``models.Model`` is called for all custom-defined models in your project because the superclass is listed as the type.

Let's add two custom conversion methods: one for a Django model and one for the built-in type ``timedelta``.  Note that we are putting the ``CustomConverter`` class in the app-level ``__init__.py`` file, but it can actually be in any file of your project that imports at Django startup.


Example 1: ``django.contrib.auth.models.User``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This first example converts the Django Model ``User``.  Out of the box, DMP already knows how to convert all Django models based on object ID.  But suppose you want to automatically convert the User object on ID *or* email address?  Let's write a custom function to do just that.

Change ``homepage/__init__.py`` to the following code:

.. code:: python

    DJANGO_MAKO_PLUS = True

    from django.http import Http404
    from django_mako_plus import set_default_converter, DefaultConverter
    import re

    class CustomConverter(DefaultConverter):

        @DefaultConverter.convert_method('auth.User')
        def convert_user(self, value, parameter, task):
            from django.contrib.auth.models import User
            try:
                # if value is all numbers, we'll assume a user id
                if re.search('^\d+$', value):
                    return User.objects.get(id=value)
                # otherwise, assume an email address
                else:
                    return User.objects.get(email=value)
                
            except User.DoesNotExist:
                raise Http404('User "{}" not found.'.format(value))

    # set as the default for all view functions
    set_default_converter(CustomConverter)

Then create ``homepage/views/userinfo.py``:

.. code:: python

    from django.conf import settings
    from django.contrib.auth.models import User
    from django_mako_plus import view_function

    @view_function
    def process_request(request, user:User):
        context = {
            'user': user,
        }
        return request.dmp_render('userinfo.html', context)
    
Finally, create ``homepage/templates/userinfo.html``:

    <%inherit file="base.htm" />

    <%block name="content">
        <ul>
            <li><strong>First Name:</strong> ${ user.first_name }</li>
            <li><strong>Last Name:</strong> ${ user.last_name }</li>
            <li><strong>Email:</strong> ${ user.email }</li>
        </ul>
    </%block>

When you load http://localhost:8000/homepage/userinfo/1/ in your browser, DMP will use ``convert_user()`` to convert the id to the ``User`` object.  The method queries by id because the regex pattern (all digits) matches.

Now load http://localhost:8000/homepage/userinfo/admin@me.com/ (use the email of the superuser you set up).  Again, DMP uses ``convert_user()``, but this time it queries the user object by email because the value contains more than digits.

String-Based Model Types
++++++++++++++++++++++++++++++

Since Python usually loads converter source files **before** your models are ready, you can't import models at the top of your source code.  This issue is `described in the Django documentation <https://docs.djangoproject.com/en/dev/ref/models/fields/#module-django.db.models.fields.related>`_.

In other words, the following may raise an error that models aren't ready yet:


.. code:: python

    # this fails because Django isn't ready yet
    from django.contrib.auth.models import User

    class CustomConverter(DefaultConverter):

        # this fails as well because User can't be referenced yet
        @DefaultConverter.convert_method(User)
        def convert_user(self, value, parameter, task):
            ...
   
In the above code, ``User`` is imported when the source file is loaded in to Python and again in the decorator call.  Since Django is still setting up, it raises an exception.  The solution is to use a string in ``app.Model`` format, e.g. ``"auth.User"``.  Then, import the model class within your converter method.

Using strings for types may or may not be necessary, depending on how your project imports are written.  This format is only allowed for model classes and not for other types like ``"str"``.


Return or Raise
+++++++++++++++++++++++++++++++

Your custom converter method should return a value to be sent to the view function.  Although it didn't make much sense here, we could have returned a default ``User`` object when a nonexistent id or email was sent.  Example 2 shows a good use case of returning a default value.

Alternatively, your custom converter method can raise an exception, which bubbles up to DMP and Django.  The above example catches ``User.DoesNotExist`` and immediately raises ``Http404``, which redirects the browser to the site-wide "not found" page.  This is a common pattern.  We also could have raised a ``RedirectException`` to send the browser to any page of the site, such as a table listing all users.  See the custom arguments section below for an example of raising a redirect.

Certain exceptions are automatically handled by DMP and Django.  Raising these exceptions can trigger certain behavior in the system:

* DMP handles `several redirect exceptions <topics_redirecting.html>`_.
* Django handles exceptions like `Http404 <https://docs.djangoproject.com/en/dev/topics/http/views/#the-http404-exception>`_.



Example 2: ``timedelta``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the tutorial, we `created a view function <tutorial_urlparams.html#adding-type-hints>`_ with url parameters for hour and minute.  Let's combine the two into a single parameter and write a custom converter function to handle the combined format.

Change ``homepage/__init__.py`` to the following code:

.. code:: python

    DJANGO_MAKO_PLUS = True

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

Then change ``/homepage/views/index.py`` to the following:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime, timedelta

    @view_function
    def process_request(request, delta:timedelta='0:00', forward:bool=True):
        if forward:
            now = datetime.now() + delta
        else:
            now = datetime.now() - delta
        context = {
            'now': now,
        }
        return request.dmp_render('index.html', context)

When you load http://localhost:8000/homepage/index/6:30/ in your browser, DMP will use ``convert_timedelta()`` to parse the hours and minutes from the first url parameter.


@view_function(custom='arguments')
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

View-specific settings to common converter functions as arguments in the view decorator.  For example, when parameter conversion errors occur, you may want to show a custom message or redirect to a URL instead of raising an Http404.

Like always, decorate your view function with the ``@view_function`` decorator, but this time, add any number of keyword arguments to the call.   These ``**kwargs`` are sent to the converter function in the task object, allowing you to send view-function-specific settings (kwargs) to your custom converters.

The following is a repeat of the "Extending" example above, modified to raise a redirect exception.  Note ``raise RedirectException`` in the first block and ``@view_function(redirect="/some/fallback/url/")`` in the second block.

.. code:: python

    from django_mako_plus import set_default_converter, DefaultConverter, RedirectException
    from datetime import datetime, timedelta
    import re

    class CustomConverter(DefaultConverter):

        @DefaultConverter.convert_method(timedelta)
        def convert_timedelta(self, value, parameter, task):
            if value not in ('', '-'):
                match = re.search('(\d+):(\d+)', value)
                if match is not None:
                    return timedelta(hours=int(match.group(1)), minutes=int(match.group(2)))
                else:
                    raise RedirectException(task.kwargs['redirect'])
            return timedelta(hours=0)

    # set as the default for all view functions
    set_default_converter(CustomConverter)

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime, timedelta

    @view_function(redirect="/some/fallback/url/")
    def process_request(request, delta:timedelta='0:00', forward:bool=True):
        if forward:
            now = datetime.now() + delta
        else:
            now = datetime.now() - delta
        context = {
            'now': now,
        }
        return request.dmp_render('index.html', context)

In summary, adding keyword arguments to ``@view_function(...)`` allows you set values *per view function*, which enables common converter functions to contain per-function logic.



Replacing the Default Converter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the default converter class doesn't work for you, or if one of your view functions needs special conversion, send a custom function to the ``@view_function`` decorator.  Converters can be any callable, including functions, lambdas, or classes that define ``__call__``.

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
        return request.dmp_render('index.html', context)

In this case, the converter is called twice: once for ``delta`` and once for ``forward``.  This will happen *even if the URL is too short*.  Consider how the following URLs would be handled:

+---------------------------------------------------+-------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6:30/T/``  | | ``convert('6:30', ...)`` is called for the ``delta`` parameter.             |
|                                                   | | ``convert('T', ...)`` is called for the ``forward`` parameter.              |
+---------------------------------------------------+-------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/6:30/T/1`` | | ``convert('6:30', ...)`` is called for the ``delta`` parameter.             |
|                                                   | | ``convert('T', ...)`` is called for the ``forward`` parameter.              |
|                                                   |    (the last parameter, "1", is ignored because not in the function signature |
+---------------------------------------------------+-------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/00:00/``   | | ``convert('00:00', ...)`` is called for the ``delta`` parameter.            |
|                                                   | | ``convert(True, ...)`` is called for the ``forward`` parameter              |
|                                                   |    (using the default in the function signature).                             |
+---------------------------------------------------+-------------------------------------------------------------------------------+
| ``http://localhost:8000/homepage/index/``         | | ``convert('0:00', ...)`` is called for the ``delta`` parameter              |
|                                                   |    (using the default in the function signature).                             |
|                                                   | | ``convert(True, ...)`` is called for the ``forward`` parameter              |
|                                                   |    (using the default in the function signature).                             |
+---------------------------------------------------+-------------------------------------------------------------------------------+



