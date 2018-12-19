Escaping Special Characters
===========================================

.. contents::
    :depth: 2

Mako expressions are the simplest way to include a variable in a template, and they are autoescaped for HTML by default:

.. code-block:: html+mako

    This is x: ${ x }

**Autoescaping of expressions in DMP is consistent with Django rather than Mako.**  Django autoescapes; Mako does not. Since Mako is the template engine, DMP converts the above expression to the following:

.. code-block:: html+mako

    This is x: ${ x | h }

If ``x`` is the string ``'<div>'``, the rendered template will contain ``&lt;div&gt;``.


A Little Background
------------------------

As described in the `Mako documentation <http://docs.makotemplates.org/en/latest/filtering.html>`_, expressions can be filtered using modifer tokens like the following:

.. code-block:: html+mako

    ## html escaped (automatic in DMP)
    ${ x | h }

    ## url escaped:
    ${ someurl | u }

    ## using django syntax in the expression
    <%! from django_mako_plus import django_syntax %>
    ${ '{{ name }}' | django_syntax(local) }

Python Blocks
-----------------------------

Python blocks, denoted with ``<% ... %>``, are not escaped automatically.  Since you are directly writing code with this method, DMP doesn't modify things.

If you need to html escape some outupt in your block, use something like the following:

.. code-block:: html+mako

    <%! from django.utils.html import conditional_escape %>
    <%
        for i in range(10):
            s = '{} < 5 is {}'.format(i, i < 5)
            context.write(conditional_escape(s))
    %>

Disabling per Expression
-------------------------------
You can stop all filtering/autoescaping for any expression with the ``n`` token:

.. code-block:: html+mako

    ## autoescaping disabled
    ${ x | n }


Disabling per Block
----------------------------
This method of disabling is patterned after the Django ``autoescape off`` tag.  It enables/disables escaping within a template block.

The code below first aliases the name ``dmp`` to DMP's tag module, which contains both ``autoescape_on`` and ``autoescape_off``.  For more information about using tag modules, see the `Mako documentation <http://docs.makotemplates.org/en/latest/defs.html>`_.

.. code-block:: html+mako

    <%namespace name="dmp" module="django_mako_plus.tags"/>

    <%dmp:autoescape_off>
        ${ '<b>This will be bolded. It will not be escaped.</b>' }

        <%dmp:autoescape_on>
            You can turn autoescaping back on, too.
            ${ '<b>This will not be bolded.  It will be escaped like normal.</b>' }
        </%dmp:autoescape_on>

        ${ '<b>Back to bold!</b>' }
    </%dmp:autoescape_off>



Disabling by Marking Safe
----------------------------------------
Just like in Django, any string can be marked as "safe" for html with ``mark_safe()``:

.. code-block:: python

    from django_mako_plus import view_function
    from django.utils.html import mark_safe

    @view_function
    def process_request(request):
        context = {
            'escapemenot': mark_safe('<b>This will be bolded. It will not be escaped.</b>'),
        }
        return request.dmp.render('index.html', context)

In your template (``index.html``):

.. code-block:: html+mako

    This will display directly, even though autoescaping is otherwise enabled:
    ${ escapemenot }


Disabling Globally
----------------------------

You can disable autoescaping project-wide by changing a DMP setting in ``settings.py``:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'AUTOESCAPE': False,
                ...
            }
        }
    ]
