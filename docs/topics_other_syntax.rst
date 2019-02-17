Combining Django and Mako Templates
=============================================================

In both Django and Mako, templates can call other templates, essentially including one rendered template within another. Using built-in and DMP tags, you can cross include Mako within Django and Django within Mako.

    For example, suppose you have a DMP site and want to use a third-party navigation/menu app (written using Django templates). You need to call the third-party app's Django-syntax template from your DMP-based code. Calling Django from Mako is shown in #2 below.

Include Tags
-------------------------

The following examples show how to include templates in various combinations of syntax:

View function (context includes *navitems* list):
    ``index.py``

    .. code-block:: html+mako

        @view_function
        def process_request(request):
            context = {
                navitems: ...
            }
            return request.dmp.render('index.html', context)



1. Mako calling a Mako template:
    ``index.html (Mako)``

    .. code-block:: html+mako

        ## must specify navitems explicitly (per the Mako tag docs)
        <html>
        <body>
            <%include file="bsnav.html" args="theme='dark', size='lg', navitems='${navitems}'" />
        </body>
        </html>

    ``bsnav.html (Mako):``

    .. code-block:: html+mako

        ## must specify page args (per the Mako tag docs)
        <%page args="theme, size, navitems" />
        <nav class="navbar navbar-expand-${ size } navbar-${ theme } bg-${ theme }">
            <ul class="navbar-nav">
                %for item in navitems:
                    <li class="nav-item"><a class="nav-link" href="${ item.link }">${ item.name }</a></li>
                %endfor
            </ul>
        </nav>


2. Mako calling a Django template:
    ``index.html (Mako)``

    .. code-block:: html+mako

        <%namespace name="dmp" module="django_mako_plus.tags"/>
        <html>
        <body>
            <%dmp:django_include template_name="bsnav.html" theme="dark" size="lg" />
        </body>
        </html>

    ``bsnav.html (Django):``

    .. code-block:: html+django

        <nav class="navbar navbar-expand-{{ size }} navbar-{{ theme }} bg-{{ theme }}">
            <ul class="navbar-nav">
                {% for item in navitems %}
                    <li class="nav-item"><a class="nav-link" href="{{ item.link }}">{{ item.name }}</a></li>
                {% endfor %}
            </ul>
        </nav>


3. Django calling a Django template:
    ``index.html (Django)``

    .. code-block:: html+django

        <html>
        <body>
            {% include "homepage/bsnav_dj.html" with theme="dark" size="lg" %}
        </body>
        </html>

    ``bsnav.html (Django):``

    .. code-block:: html+django

        <nav class="navbar navbar-expand-{{ size }} navbar-{{ theme }} bg-{{ theme }}">
            <ul class="navbar-nav">
                {% for item in navitems %}
                    <li class="nav-item"><a class="nav-link" href="{{ item.link }}">{{ item.name }}</a></li>
                {% endfor %}
            </ul>
        </nav>


4. Django calling a Mako template:
    ``index.html (Django)``

    .. code-block:: html+django

        <html>
        <body>
            {% load django_mako_plus %}
            {% dmp_include "homepage/bsnav.html" with theme="dark" size="lg" %}
        </body>
        </html>

    ``bsnav.html (Mako):``

    .. code-block:: html+mako

        <nav class="navbar navbar-expand-${ size } navbar-${ theme } bg-${ theme }">
            <ul class="navbar-nav">
                %for item in navitems:
                    <li class="nav-item"><a class="nav-link" href="${ item.link }">${ item.name }</a></li>
                %endfor
            </ul>
        </nav>



Django Syntax Blocks
------------------------

There may be times when you need or want to call real, Django tags or include Django template syntax in your DMP templates. In other words, you need to combine Mako, Django, and even Jinja2 syntaxes in the *same* template.

This situation can occur when you include a third-party app in your project, and the new library provides Django tags.  You need to reference these tags within your DMP templates.

    Like the Cataclyst time bomb, this is a kludge that should be used sparingly.

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While context variables are global anywhere in your template, variables created in templates are available only in the block they are created. These temporary variables don't jump scope into other blocks.

To send variables from a parent block to a child block, send them in the block signature:

weather.html
    .. code-block:: html+mako

        <% pressure = 29.84 %>

        <%block filter="django_syntax(local)">
            The pressure is undefined here: huh? pressure? whaaa?
        </%block>

        <%block filter="django_syntax(local, pressure=pressure)">
            Django now knows the current pressure is {{ pressure }}.
        </%block>


Jinja2 or (( insert engine here )) Syntax Blocks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If Jinja2 is needed, replace the filters with ``jinja2_syntax(context)`` in the above examples. If another engine is needed, replace the filter with ``template_syntax(context, 'engine name')`` as specified in ``settings.TEMPLATES``. DMP will render with the appriate engine and put the result in your HTML page.

weather.html
    .. code-block:: text

        <% pressure = 29.84 %>

        <%block filter="jinja2_syntax(local, pressure=pressure)">
            {% if pressure < 29 %}
                A storm might be coming!
            {% endif %}
        </%block>
