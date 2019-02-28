.. _topics_modules:

Python Imports in Templates
====================================

It's easy to import Python and PyPI (pip) modules in your Mako templates.

Use a template-level block:
    .. code-block:: html+mako

        <% from datetime import datetime %>

or a module-level block:
    .. code-block:: html+mako

        <%! from decimal import Decimal %>


The Gory Details
-----------------------
When Mako compiles templates, it actually writes a Python code file: all of your HTML code goes into a function named ``def render_body()``. It's actually this function that gets run each time the template is "rendered". This template:

app/templates/template.html
    .. code-block:: html+mako

        <%! from decimal import Decimal %>
        <% from datetime import datetime %>
        <h1>My Page</h1>
        The even numbers:
        %for i in range(10):
            %if i % 2 == 0:
                <p>${ i }: Mako is the bomb, amirite?!?</p>
            %endif
        %endfor

Turns into the following function. Note where the two import statements are placed. That's the full power of the exclamation point!

app/templates/__dmpcache__/template.html.py:
    .. code-block:: python

        from decimal import Decimal

        def render_body(context,**pageargs):
            __M_caller = context.caller_stack._push_frame()
            try:
                __M_locals = __M_dict_builtin(pageargs=pageargs)
                self = context.get('self', UNDEFINED)
                range = context.get('range', UNDEFINED)
                __M_writer = context.writer()
                __M_writer('\n')

                from datetime import datetime

                __M_locals_builtin_stored = __M_locals_builtin()
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['datetime'] if __M_key in __M_locals_builtin_stored]))
                __M_writer('\n<h1>My Page</h1>\nThe even numbers:\n')
                for i in range(10):
                    if i % 2 == 0:
                        __M_writer('        <p>')
                        __M_writer(django_mako_plus.ExpressionPostProcessor(self)( i ))
                        __M_writer(': Mako is the bomb, amirite?!?</p>\n')
                return ''
            finally:
                context.caller_stack._pop_frame()


Template-level blocks are placed within the body of the ``render_body`` method, while module-level blocks are placed at the top of the file. In effect, it's the same as writing an import statement within a function vs. an import statement at the top of a module.

Although it probably doesn't matter too much, the module-level block ``<%! import ... %>`` is usually best for import statements.


Global Template Imports
--------------------------

There may be some modules, such as ``re`` or ``decimal`` that are so useful you want them available in every template of your site. In settings.py, add these to the ``DEFAULT_TEMPLATE_IMPORTS`` variable:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                DEFAULT_TEMPLATE_IMPORTS = [
                    'import os, os.path, re',
                    'from decimal import Decimal',
                ],
                ...
            }
        }
    ]


Any entries in this list will be automatically included in templates throughout all apps of your site. With the above imports, you'll be able to use ``re`` and ``Decimal`` and ``os`` and ``os.path`` anywhere in any .html, .cssm, and .jsm file.

    Whenever you modify DMP settings, and especially in this case, be sure to **clean out your cached templates**. Mako needs to regenerate all of your templates with the new import statements at the top. See the next section on cleaning up for the command.


Cleaning Up
-----------

DMP caches its compiled mako+templates in subdirectories of each app. The default locations for each app are ``app/templates/__dmpcache__``, ``app/scripts/__dmpcache__``, and ``app/styles/__dmpcache__``, although the exact name depends on your settings.py. Normally, these cache directories are hidden and warrant your utmost apathy. However, there are times when DMP fails to update a cached template as it should. Or you might just need a pristine project without these generated files. This can be done with a Unix find command or through DMP's ``dmp_cleanup`` management command:

::

    # see what would be be done without actually deleting any cache folders
    python3 manage.py dmp_cleanup --trial-run

    # really delete the folders
    python3 manage.py dmp_cleanup


With this management command, add ``--verbose`` to the command to include messages about skipped files, and add ``--quiet`` to silence all messages (except errors).
