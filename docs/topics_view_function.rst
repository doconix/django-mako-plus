Customizing @view_function
--------------------------------------

Since the ``@view_function`` decorator must be placed on all view functions in your system, it's a great place to do pre-endpoint logic.  ``@view_function`` was intentionally programmed as a class-based decorator so you can extend it.

    Django provide several ways to insert logic into the request process, so be sure to consider which is the cleanest approach for your situation: the approach here, middleware, signals, or another method.


Using Keyword Arguments
=============================

Although we normally specify ``@view_function`` without any arguments, it can take an arbitrary number of keyword arguments. The following are some examples:

.. code-block:: python

    # the normal decorator
    @view_function

    # ensure the user has a role of "mentor"
    @view_function(role='mentors')

    # require authenticated access, set response type to text/html
    @view_function(auth_required=True, mimetype='text/html')

Through a simple extension, you can access the parameters above and do custom logic--just before process_request is called.

Example: Authenticated Endpoints
=====================================

Suppose your site requires authentication on nearly every endpoint in the system. Normally, you'd add Django's ``@login_required`` decorator to endpoints, like this:

.. code-block:: python

    from django.contrib.auth.decorators import login_required
    from django_mako_plus import view_function

    @login_required
    @view_function
    def process_request(request):
        ...

Rather than hope every endpoint gets marked with the decorator, let's modify DMP's view function decorator to require access by default. Create the following in a file called ``lib/router.py``:

.. code-block:: python

    from django.conf import settings
    from django.http import HttpResponseRedirect
    from django_mako_plus import view_function
    import inspect


    class web_endpoint(view_function):
        '''Marks a view function in the system (with auth required by default)'''
        def __init__(self, decorated_func, auth_required=True, *args, **kwargs):
            self.auth_required = auth_required
            super().__init__(decorated_func, *args, **kwargs)

        def __call__(self, request, *args, **kwargs):
            # ensure authenticated
            if self.auth_required and request.user.is_anonymous:
                return HttpResponseRedirect(settings.LOGIN_URL)

            # allow the call to continue
            return super().__call__(request, *args, **kwargs)


Then, use this decorator **insead** of the normal view function decorator. In fact, do a global search and replace of ``@view_function``, and replace it with ``@secure_function``.

.. code-block:: python

    from lib.router import secure_function

    @secure_function
    def process_request(request):
        ...

When DMP calls your view functions, it now runs ``lib.router.secure_function.__call__``. Our function redirects if the current user isn't authenticated yet. If the user is authenticated, we call the super's ``__call__`` method, which runs the view function. Just like that, every endpoint in the system is protected by default.

For endpoints that need to allow anonymous access, the ``auth_required`` parameter signals that everyone can pass (yep, even balrogs). The login endpoint looks like this:


.. code-block:: python

    from lib.router import secure_function

    @secure_function(auth_required=False)
    def process_request(request):
        # login endpoint, so everyone allowed!
