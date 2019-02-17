Using Django/Jinja2 in Mako Templates (and vice-versa)
=============================================================


There may be times when you need or want to call real, Django tags or include Django template syntax in your DMP templates. In other words, you need to combine Mako, Django, and even Jinja2 syntaxes in the *same* template.

This situation can occur when you include a third-party app in your project, and the new library provides Django tags.  You need to reference these tags within your DMP templates.

    Like the Cataclyst time bomb, this is a kludge that should be used sparingly.

Becoming Bilingual (settings.py):
    .. code-block:: python

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

Now clear out the compiled templates caches:
    .. code-block:: bash

        python3 manage.py dmp_cleanup

Using Django Syntax
------------------------

:A Django expression:
    .. code-block:: html+mako

        ${ '{{ name }}' | django_syntax(local) }

:A block of Django:
    .. code-block:: html+mako

        ## Switch to Django syntax for this block only
        <%block filter="django_syntax(local)">
            {% if athlete_list %}
                Number of athletes: {{ athlete_list|length }}
            {% elif athlete_in_locker_room_list %}
                Athletes should be out of the locker room soon!
            {% else %}
                No athletes.
            {% endif %}
        </%block>

        ## continue Mako syntax...


:A block of Django, with variables created in Mako:
    .. code-block:: html+mako

        ## Look Ma! Mako's creating data that Django's using...
        <% titles = [ 'First', 'Second', 'Third' ] %>

        ## Switch to Django syntax for this block
        <%block filter="django_syntax(local, titles=titles)">
            {% for title in titles %}
                <h2>{{ title|upper }}</h2>
            {% endfor %}
        </%block>

        ## continue Mako syntax...

:A Crispy Form, used as directed with the regular Django tag:
    .. code-block:: html+mako

        <%block filter="django_syntax(local)">
            {% load crispy_forms_tags %}
            <form method="post" class="uniForm">
                {{ my_formset|crispy }}
            </form>
        </%block>


The ``local`` Parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the above examples, you'll notice the use of ``local`` when switching to Django syntax. This is a global Mako variable (available anywhere in every template). It provides the local context so DMP can temporarily initialize Django. Just include it the way you see above, and all your dreams will come true.


Using Context Variables
---------------------------------------

Embedded Django code has access to any variable passed to your template. In other words, Django code in your template has access to anything your view sends:

weather.py
    .. code-block:: python

        @view_function
        def process_request(request):
            context = {
                'temp': 17,
            }
            return request.dmp.render('weather.html', context)

weather.html
    .. code-block:: html+mako

        Mako says it's ${ temp } degrees celsius.

        <%block filter="django_syntax(local)">
            Django also says it's {{ temp }} degrees celsius.
        </%block>

        Mako can also say it's ${ round((temp * 9/5) + 32) } degrees fahrenheit.


Using Template Variables
---------------------------------

While context variables are global anywhere in your template, variables created in templates are available only in the block they are created. These temporary variables don't jump scope into other blocks (that's the way Mako is programmed).

To send variables from a parent block to a child block, send them in the block signature:

weather.html
    .. code-block:: html+mako

        <% pressure = 29.84 %>

        <%block filter="django_syntax(local)">
            Django doesn't know the pressure in this block!
        </%block>

        <%block name="sub_block">
            Mako has the same restrictions - pressure is not in scope here.
        </block>

        <%block filter="django_syntax(local, pressure=pressure)">
            Django now knows the current pressure is {{ pressure }}.
        </%block>


Jinja2 or ((insert template engine))
------------------------------------------------------------------------------

If Jinja2 is needed, replace the filters with ``jinja2_syntax(context)`` in the above examples. If another engine is needed, replace the filter with ``template_syntax(context, 'engine name')`` as specified in ``settings.TEMPLATES``. DMP will render with the appriate engine and put the result in your HTML page.

weather.html
    .. code-block:: text

        <% pressure = 29.84 %>

        <%block filter="jinja2_syntax(local, pressure=pressure)">
            {% if pressure < 29 %}
                A storm might be coming!
            {% endif %}
        </%block>


Reverse That: DMP in Django Templates
-------------------------------------------

Thus far, we've shown how to embed other tags and template languages within DMP templates.  The opposite is supported as well: embedding DMP snippets within Django templates.

Suppose a third party contains a "normal" Django template -- one that uses the standard Django syntax instead of Mako syntax. In customizing these templates, you may want to include DMP templates.  Django has an ``include`` template tag, but that's for Django templates.  That's where DMP's ``dmp_include`` tag comes in.

For example, suppose your Django template, ``django_template.html`` needs to include the Mako-syntax ``navigation_snippet.htm`` in app ``homepage``.  Put the following inside ``django_template.html``:

django_template.html
    .. code-block:: html+mako

        {% Note the normal Django template syntax %}
        <html>
        <body>
            ...
            {% load django_mako_plus %}
            {% dmp_include "homepage" "navigation_snippet.htm" %}
        </body>
        </html>

You can also specify a ``def`` or ``block`` within the navigation snippet:

django_template.html
    .. code-block:: html+mako

        {% Now including just a single def/block from the Mako template %}
        <html>
        <body>
            ...
            {% load django_mako_plus %}
            {% dmp_include "homepage" "navigation_snippet.htm" "someblock" %}
        </body>
        </html>
