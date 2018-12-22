Customizing @view_function
--------------------------------------

.. contents::
    :depth: 2


The ``@view_function`` decorator annotates functions in your project that are web-accessible.  Without it, clients could use DMP's conventions to call nearly any function in your system.

The decorator implementation itself is fairly straightforward.  However, as a decorator for all endpoints in your system, it is a great place to do pre-endpoint work.  ``@view_function`` was intentionally programmed as a class-based decorator so you can extend it.


Using Keyword Arguments
=============================

Although we normally specify ``@view_function`` without any arguments, it can take an arbitrary number of keyword arguments.  Any extra arguments are placed in ``self.decorator_args`` and ``self.decorator_kwargs``.

For this example, lets check user groups in the view function decorator.  We really should use permission-based security rather than group-based security.  And Django already comes with the ``@require_permission`` decorator.  And Django has ``process_view`` middleware you could plug into.  So even if this example is a little contrived, let's go with it. We've found places where, despite the other options, this is the right place to do pre-view work.

We'll override both the constructor and the __call__ methods in this example so you can see both:

.. code-block:: python

    from django_mako_plus import view_parameter

    class site_endpoint(view_function):
        '''Customized view function decorator'''

        def __init__(self, f, require_role=None, *args, **kwargs):
            '''
            This runs as Python loads the module containing your view function.
            You can specify new parameters (like require_role here) or just use **kwargs.
            Don't forget to include the function as the first argument.
            '''
            super().__init__(self, f, *args, **kwargs)
            self.require_role = require_role

        def __call__(self, request, *args, **kwargs):
            '''
            This runs every time the view function is accessed by a client.
            Be sure to return the result of super().__call__ as it is your
            view function's response.
            '''
            # check roles
            if self.require_role:
                if request.user.is_anonymous or request.user.groups.filter(name=self.require_role).count() == 0:
                    return HttpResponseRedirect('/login/')

            # call the view function
            return super().__call__(request, *args, **kwargs)

In ``homepage/views/index.py``, use your custom decorator.

.. code-block:: python

    from .some.where import site_endpoint

    @site_endpoint(require_role='mentors')
    def process_request(request):
        ...

In the above example, overriding ``__init__`` isn't technically necessary.  Any extra ``*args`` and ``**kwargs`` in the constructor call are placed in ``self.decorator_args`` and ``self.decorator_kwargs``.  So instead of explictily listing ``require_role`` in the argument list, we could have used ``self.decorator_kwargs.get('require_role')``.  I listed the parameter explicitly for code clarity.
