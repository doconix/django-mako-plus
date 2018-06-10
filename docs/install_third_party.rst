Integrating Third-Party Apps
=======================================================

Since most third-party apps use standard Django routing and template syntax, new users to DMP often worry about conflicts between the two engines.  Have no fear, they work together just like Windows and Linux!  (just kidding, they work great together)

Third-party apps often come with custom Django tags that you include in templates.  Since those tags are likely in Django format (and not Mako), you'll have to slightly translate the documentation for each library.

In most cases, third-party functions can be called directly from Mako. For example, the custom form tag in the `Django Paypal library <http://django-paypal.readthedocs.io/>`_ converts easily to Mako syntax:

-  The docs show: ``{{ form.render }}``
-  You use: ``${ form.render() }``

In the above example, we're simply using regular Python in DMP to call the tags and functions within the third party library.

If the tag can't be called using regular Python, you can usually inspect the third-party tag code.  In most libraries, tags just call Python functions because since Django doesn't allow direct Python in templates.  In the `Crispy Form library <http://django-crispy-forms.readthedocs.io/>`_, you can simply import and call its ``render_crispy_form`` function directly.  This skips over the Django tag entirely:

::

    <%! from crispy_forms.utils import render_crispy_form %>

    <html>
    <body>
        <form method="POST">
            ${ csrf_input }
            ${ render_crispy_form(form) }
        </form>
    </body>
    </html>


If you call the ``render_crispy_form`` method in many templates, you may want to add the import to ``DEFAULT_TEMPLATE_IMPORTS`` in your ``settings.py`` file. Once this import exists in your settings, the function will be globally available in every template on your site.

    Whenever you modify the DMP settings, be sure to clean out your cached templates with ``python3 manage.py dmp cleanup``. This ensures your compiled templates are rebuilt with the new settings.


Using Third-Party Tags
------------------------------

There may be times when you can't call a third-party function.  Or perhaps you just want to use the Django tags as the third-party library intended, dammit!

Venture over to `Django Syntax and Tags </topics_other_syntax.html>`_ to see how to include Django-style tags in your Mako templates.
