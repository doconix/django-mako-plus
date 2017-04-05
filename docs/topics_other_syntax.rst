Integrating Third-Party Apps (Django/Jinja2 syntax)
=======================================================

In most cases, third-party functionality can be called directly from Mako. For example, use the `Django Paypal <http://django-paypal.readthedocs.io/>`__ form by converting the Django syntax to Mako:

-  The docs show: ``{{ form.render }}``
-  You use:\ ``${ form.render() }``

In other words, use regular Python in DMP to call the tags and functions within the third party library. For example, you can render a `Crispy Form <http://django-crispy-forms.readthedocs.io/>`__ by importing and calling its ``render_crispy_form`` function right within your template.

For example, suppose your view constructs a Django form, which is then sent to your template via the context dictionary. Your template would look like this:

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

    Whenever you modify the DMP settings, be sure to clean out your
    cached templates with ``python manage.py dmp_cleanup``. This ensures
    your compiled templates are rebuilt with the new settings.

However, there may be times when you need or want to call real, Django tags. For example, although `Crispy Forms' <http://django-crispy-forms.readthedocs.io/>`__ functions can be called directly, you may want to use its custom tags.

To enable alternative syntaxes, uncomment (or add) the following to your ``settings.py`` file:

.. code:: python

    'DEFAULT_TEMPLATE_IMPORTS': [
        'from django_mako_plus import django_syntax, jinja2_syntax, alternate_syntax
    ],

Then clear out the compiled templates caches:

::

    python manage.py dmp_cleanup

Now that the functions are imported, you can include a Django expression or embed an entire block within your Mako template by using a filter:

::

    ## Expression containing Django template syntax (assuming name was created in the view.py)
    ${ '{{ name }}' | django_syntax(self) }

    ## Full Django code block, with Mako creating the variable first
    <% titles = [ 'First', 'Second', 'Third' ] %>
    <%block filter="django_syntax(self, titles=titles)">
        {% for title in titles %}
            <h2>
                {{ title|upper }}
            </h2>
        {% endfor %}
    </%block>

    ## Third-party, crispy form tags (assume my_formset was created in the view.py)
    <%block filter="django_syntax(self)">
        {% load crispy_forms_tags %}
        <form method="post" class="uniForm">
            {{ my_formset|crispy }}
        </form>
    </%block>

The ``self`` parameter passes your context variables to the Django render call. It is a global Mako variable (available in any template), and it is always included in the filter. In other words, include ``self`` every time as shown in the examples above.

Jinja2 or ((insert template engine))
------------------------------------------------------------------------------

If Jinja2 is needed, replace the filter with ``jinja2_syntax(context)`` in the above examples. If another engine is needed, replace the filter with ``template_syntax(context, 'engine name')`` as specified in ``settings.TEMPLATES``. DMP will render with the appriate engine and put the result in your HTML page.

Local Variables
---------------------------------------

Embedded template code has access to any variable passed to your temple (i.e. any variable in the context). Although not an encouraged practice, variables are sometimes created right in your template, and faithful to the Mako way, are not accessible in embedded blocks.

You can pass locally-created variables as kwargs in the filter call. This is done with ``titles=titles`` in the Django code block example above.
