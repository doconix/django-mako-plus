CSRF Tokens
====================

In support of the Django CSRF capability, DMP includes ``csrf_token`` and ``csrf_input`` in the context of every template. Following `Django's lead <https://docs.djangoproject.com/en/dev/ref/csrf/>`__, this token is always available and cannot be disabled for security reasons.

However, slightly different than Django's default templates (but following `Jinja2's lead <https://docs.djangoproject.com/en/dev/ref/csrf/#using-csrf-in-jinja2-templates>`__), use ``csrf_input`` to render the CSRF input:

::

    <form action="" method="post">
        ${ csrf_input }
        ...
    </form>

    Since the CSRF token requires a request object, using an empty
    request ``dmp_render(None, ...)`` prevents the token from being
    included in your templates.
