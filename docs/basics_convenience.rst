Convenience Functions
===========================================

.. contents::
    :depth: 2


You might be wondering: Can I use a dynamically-found app? What if I need a template object? Can I render a file directly?

Use the DMP convenience functions to be more dynamic, to interact directly with template objects, or to render a file of your choosing.

*Render a file from any app's template directory:*

.. code:: python

    from django_mako_plus import render_template
    mystr = render_template(request, 'homepage', 'index.html', context)

*Render a file from a custom directory within an app:*

.. code:: python

    from django_mako_plus import render_template
    mystr = render_template(request, 'homepage', 'custom.html', context, subdir="customsubdir")

*Render a file at any location, even outside of your project:*

.. code:: python

    from django_mako_plus import render_template_for_path
    mystr = render_template_for_path(request, '/var/some/dir/template.html', context)

*Get a template object for a template in an app:*

.. code:: python

    from django_mako_plus import get_template
    template = get_template('homepage', 'index.html')

*Get a template object at any location, even outside your project:*

.. code:: python

    from django_mako_plus import get_template_for_path
    template = get_template_for_path('/var/some/dir/template.html')

*Get a lower-level Mako template object (without the Django template wrapper):*

.. code:: python

    from django_mako_plus import get_template_for_path
    template = get_template_for_path('/var/some/dir/template.html')
    mako_template = template.mako_template

See the `Mako documentation <http://www.makotemplates.org/>`__ for more information on working directly with Mako template objects. Mako has many features that go well beyond the DMP interface.

    The convenience functions are perfectly fine if they suit your needs, but the ``request.dmp.render`` function described at the beginning of the tutorial is likely the best choice for most users because it doesn't hard code the app name. The convenience functions are not Django-API compliant.


