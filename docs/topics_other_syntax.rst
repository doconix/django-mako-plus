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
        'from django_mako_plus import django_syntax, jinja2_syntax, alternate_syntax',
    ],

Then clear out the compiled templates caches:

::

    python manage.py dmp_cleanup

Next, ensure the engine you are using is enabled in ``settings.py``.  For example, including Django syntax means including the following:

.. code:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            # all the other settings here
        },
        {
            'NAME': 'django',
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

Now that the functions are imported, you can include a Django expression or embed an entire block within your Mako template by using a filter:

::

    ## Expression containing Django template syntax (assuming name was created in the view.py)
    ${ '{{ name }}' | django_syntax(local) }

    ## Full Django code block, with Mako creating the variable first
    <% titles = [ 'First', 'Second', 'Third' ] %>
    <%block filter="django_syntax(local, titles=titles)">
        {% for title in titles %}
            <h2>
                {{ title|upper }}
            </h2>
        {% endfor %}
    </%block>

    ## Third-party, crispy form tags (assume my_formset was created in the view.py)
    <%block filter="django_syntax(local)">
        {% load crispy_forms_tags %}
        <form method="post" class="uniForm">
            {{ my_formset|crispy }}
        </form>
    </%block>

The ``local`` parameter passes your context variables to the Django render call. It is a global Mako variable (available in any template), and it is always included in the filter. In other words, include ``local`` every time as shown in the examples above.

Jinja2 or ((insert template engine))
------------------------------------------------------------------------------

If Jinja2 is needed, replace the filter with ``jinja2_syntax(context)`` in the above examples. If another engine is needed, replace the filter with ``template_syntax(context, 'engine name')`` as specified in ``settings.TEMPLATES``. DMP will render with the appriate engine and put the result in your HTML page.

    Don't forget to include the ``TEMPLATES`` declaration for Jinja2 in your ``settings.py`` file.

Local Variables
---------------------------------------

Embedded template code has access to any variable passed to your temple (i.e. any variable in the context). Although not an encouraged practice, variables are sometimes created right in your template, and faithful to the Mako way, are not accessible in embedded blocks.

You can pass locally-created variables as kwargs in the filter call. This is done with ``titles=titles`` in the Django code block example above.

Including DMP in Django Templates
-------------------------------------------

Suppose a third party contains a "normal" Django template -- one that uses the standard Django syntax instead of Mako syntax. In customizing these templates, you may want to include DMP templates.  Django has an ``include`` template tag, but that's for Django templates.  That's where DMP's ``dmp_include`` tag comes in.

Inside a standard Django template, use the following:

::

    {% load django_mako_plus %}
    {% dmp_include "app" "template name" %}

For example, suppose your Django template, ``my_standard_template.html`` needs to include the Mako-syntax ``navigation_snippet.htm`` in app ``homepage``.  Put the follwoing inside ``my_standard_template.html``:

::
    <!-- this file is my_standard_template.html -->
    {% load django_mako_plus %}
    {% dmp_include "homepage" "navigation_snippet.htm" %}

You can also specify a ``def`` or ``block`` within the navigation snippet:

::
    <!-- this file is my_standard_template.html -->
    {% load django_mako_plus %}
    {% dmp_include "homepage" "navigation_snippet.htm" "someblock" %}
