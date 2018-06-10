Django/Jinja2 within Mako Templates
=======================================================

Django officially supports multiple template engines, even within the same project/app.  Simply list the engines you want to use, such as Django, Jinja2, and DMP, in your settings.py file.

With multiple engines, Django's ``render`` function tries each engine and uses the first one that takes a given template.  Django templates are rendered by the Django engine.  Mako templates are rendered by the DMP engine.  Jinja2 templates are rendered by the Jinja2 engine.

Becoming Bilingual
---------------------------

There may be times when you need or want to call real, Django tags or include Django template syntax in your DMP templates. In other words, you need to combine both Mako, Django, and/or Jinja2 syntaxes in the *same* template.

This situation can occur when you include a third-party app in your project, and the new library provides Django tags.  You need to reference these tags within your DMP templates.  For example, although `Crispy Forms' <http://django-crispy-forms.readthedocs.io/>`__ functions can be called directly, you may want to use its custom tags.

To enable alternative syntaxes, enable the DMP tags with the following settings.  Also ensure you have the Django template engine included.

.. code:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'OPTIONS': {
                'DEFAULT_TEMPLATE_IMPORTS': [
                    'from django_mako_plus import django_syntax, jinja2_syntax, alternate_syntax',
                ],
            }
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

Then clear out the compiled templates caches:

::

    python3 manage.py dmp cleanup

In your Mako template, include a Django expression or embed an entire block by using a Mako filter:

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

The Mako Templates web site provides more information on filters.



Jinja2 or ((insert template engine))
------------------------------------------------------------------------------

If Jinja2 is needed, replace the filters with ``jinja2_syntax(context)`` in the above examples. If another engine is needed, replace the filter with ``template_syntax(context, 'engine name')`` as specified in ``settings.TEMPLATES``. DMP will render with the appriate engine and put the result in your HTML page.

    Don't forget to include the ``TEMPLATES`` declaration for Jinja2 in your ``settings.py`` file.

Local Variables
---------------------------------------

Embedded template code has access to any variable passed to your temple (i.e. any variable in the context). Although not an encouraged practice, variables are sometimes created right in your template, and faithful to the Mako way, are not accessible in embedded blocks.

You can pass locally-created variables as kwargs in the filter call. This is done with ``titles=titles`` in the Django code block example above.


Reverse That: DMP in Django Templates
-------------------------------------------

Thus far, we've shown how to embed other tags and template languages within DMP templates.  The opposite is supported as well: embedding DMP snippets within Django templates.

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
