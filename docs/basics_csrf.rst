CSRF Tokens
====================

In support of the Django CSRF capability, DMP includes ``csrf_token`` and ``csrf_input`` in the context of every template. Following `Django's lead <https://docs.djangoproject.com/en/dev/ref/csrf/>`__, this token is always available and cannot be disabled for security reasons.

However, slightly different than Django's default templates (but following `Jinja2's lead <https://docs.djangoproject.com/en/dev/ref/csrf/#using-csrf-in-jinja2-templates>`__), use ``csrf_input`` to render the CSRF input:

::

    <form action="" method="post">
        ${ csrf_input }
        ${ form }
        <input type="submit" value="Submit" />
    </form>



Using Python Code
-----------------------------

The standard way to insert the CSRF token is with the template tag (as above).  However, suppose you are creating your forms directly using Python code, like this next example does.

The functions to create the token are actually right in Django (no need for DMP).  Here are two options:

1. ``django.template.backends.utils.csrf_input`` creates the full tag: ``<input type="hidden" name="csrfmiddlewaretoken" value="YpaAqd8LjS5j2eG...">``
2. ``django.middleware.csrf.get_token`` creates and returns the token value: ``YpaAqd8LjS5j2eG...``

Example:

.. code:: python

    from io import StringIO
    from django.template.backends.utils import csrf_input

    def render_form(request, form):
        '''Renders the form html'''
        buf = StringIO()
        buf.write('<form action="" method="post">')
        buf.write(csrf_input(request))
        buf.write(str(form))
        buf.write('<input type="submit" value="Submit" />')
        buf.write('</form>')
        return buf.getvalue()
