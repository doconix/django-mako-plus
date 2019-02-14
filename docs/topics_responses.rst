Lazy Rendering with ``TemplateResponse``
=======================================================

The Django documentation describes two template-oriented responses: `TemplateResponse <https://docs.djangoproject.com/en/dev/ref/template-response/>`_ and  `SimpleTemplateResponse <https://docs.djangoproject.com/en/dev/ref/template-response/>`_. These specialized responses support lazy rendering at the last possible moment. This allows decorators or middleware to modify the response after creating but before template rendering.

DMP can be used with template responses, just like any other template engine.

Method 1: Template String
------------------------------

Specify the DMP template using ``app/template`` format. This method uses `Django-style format </basics_django.html>`_:

.. code-block:: python

    from django_mako_plus import view_function
    from django.template.response import TemplateResponse

    @view_function
    def process_request(request):
        ...
        context = {...}
        return TemplateResponse(request, 'homepage/index.html', context)



Method 2: Template Object
--------------------------------

Alternatively, use a template object in the current app. This method uses DMP-style format:

.. code-block:: python

    from django_mako_plus import view_function
    from django.template.response import TemplateResponse

    @view_function
    def process_request(request):
        ...
        context = {...}
        template = request.dmp.get_template('index.html')
        return TemplateResponse(request, template, context)
