.. _topics_paths:

Inheritance Paths and Template Location
===========================================

.. contents::
    :depth: 2

In addition, you can also render the `normal Django API way <basics_django.html>`_.

Template Inheritance Across Apps
--------------------------------

You may have noticed that this tutorial has focused on a single app. Most projects consist of many apps. For example, a sales site might have an app for user management, an app for product management, and an app for the catalog and sales/shopping-cart experience. All of these apps probably want the same look and feel, and all of them likely want to extend from the **same** ``base.htm`` file.

When you run ``python3 manage.py dmp_startapp <appname>``, you get **new** ``base.htm`` and ``base_ajax.htm`` files each time. This is done to get you started on your first app. On your second, third, and subsequent apps, you probably want to delete these starter files and instead extend your templates from the ``base.htm`` and ``base_ajax.htm`` files in your first app.

In my projects, I usually place all the common files in the ``homepage`` app. I delete ``base.htm`` and ``base_ajax.htm`` from all other apps. Homepage contains the common html code, site-wide CSS, and site-wide Javascript.

DMP supports cross-app inheritance by including your project root (e.g. ``settings.BASE_DIR``) in the template lookup path. All you need to do is use the full path (relative to the project root) to the template in the inherits statement.

Suppose I have the following app structure:

::

    myproject/
        account/
            __init__.py
            media/
            scripts/
            styles/
            templates/
                login.html
            views/
                __init__.py
        homepage/
            __init__.py
            media/
            scripts/
            styles/
            templates/
                base_ajax.htm
                base.htm
                index.html
            views/
                __init__.py

I set ``account/templates/login.html`` to extend from ``homepage/templates/base.htm`` using the following code at the top of the template:

.. code-block:: html+mako

    <%inherit file="/homepage/templates/site_base.htm" />

Again, the front slash in the name above tells DMP to start the lookup at the project root.

    In fact, my pages are often three inheritance levels deep:
    ``homepage/templates/base.htm -> account/templates/app_base.htm -> account/templates/index.html``
    to provide for site-wide page code, app-general page code, and specific
    page code.



Templates in Other Apps
--------------------------

Most of the time, you'll render templates in the request's current app. This is easy with ``request.dmp.render(...)``.

Infrequently, you'll likely need to render templates in apps other than the current one. There's two ways to do it:

Method 1: Use the ``render_template`` convenience function:
    .. code-block:: python

        from django.conf import settings
        from django.http import HttpResponse
        from django_mako_plus import view_function, render_template
        from datetime import datetime

        @view_function
        def process_request(request):
            context = {
                'now': datetime.now(),
            }
            # replace 'homepage' with the name of any DMP-enabled app:
            return HttpResponse(render_template(request, 'homepage', 'index.html', context))

Method 2: Use the standard Django API:
    .. code-block:: python

        from django.conf import settings
        from django.shortcuts import render
        from django_mako_plus import view_function
        from datetime import datetime

        @view_function
        def process_request(request):
            context = {
                'now': datetime.now(),
            }
            # replace 'homepage' with the name of any DMP-enabled app:
            return render(request, 'homepage/index.html', context)


Content Types and Status Codes
--------------------------------

The ``request.dmp.render()`` function determines the mime type from the template extension and returns a *200* status code. What if you need to return JSON, CSV, or a 404 not found?  The function takes these parameters too. A few examples:

.. code-block:: python

    from django.http import HttpResponse

    # return CSV
    return request.dmp.render('my_csv.html', {}, content_type='text/csv')

    # return a custom error page
    return request.dmp.render('custom_error_page.html', {}, status=404)

    # specify a different template charset (or set globally in settings.py)
    return request.dmp.render('im_old.html', {}, content_type='cp1252')

Changing the Template Location (globally)
--------------------------------------------

Suppose your templates are located in a directory outside your normal project root. For whatever reason, you don't want to put your templates in the app/templates directory.

Case 1: Templates Within Your Project Directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the templates you need to access are within your project directory, no extra setup is required. Simply reference those templates relative to the root project directory. For example, to access a template located at BASE\_DIR/homepage/mytemplates/sub1/page.html, use the following:

.. code-block:: python

    return request.dmp.render('/homepage/mytemplates/sub1/page.html', context)

Note the starting slash on the path. That tells DMP to start searching at your project root.

Don't confuse the slashes in the above call with the slash used in Django's ``render`` function. When you call ``render``, the slash separates the app and filename. The above call uses ``request.dmp.render``, which is a different function. You should really standardize on one or the other throughout your project.

Case 2: Templates Outside Your Project Directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose your templates are located on a different disk or entirely different directory from your project. DMP allows you to add extra directories to the template search path through the ``TEMPLATES_DIRS`` setting. This setting contains a list of directories that are searched by DMP regardless of the app being referenced. To include the ``/var/templates/`` directory in the search path, set this variable as follows:

.. code-block:: python

    'TEMPLATES_DIRS': [
       '/var/templates/',
    ],

Suppose, after making the above change, you need to render the '/var/templates/page1.html' template:

.. code-block:: python

    return request.dmp.render('page1.html', context)

DMP will first search the current app's ``templates`` directory (i.e. the normal way), then it will search the ``TEMPLATES_DIRS`` list, which in this case contains ``/var/templates/``. Your ``page1.html`` template will be found and rendered.



Cleaning Up
-----------

DMP caches its compiled mako+templates in subdirectories of each app. The default locations for each app are ``app/templates/__dmpcache__``, ``app/scripts/__dmpcache__``, and ``app/styles/__dmpcache__``, although the exact name depends on your settings.py. Normally, these cache directories are hidden and warrant your utmost apathy. However, there are times when DMP fails to update a cached template as it should. Or you might just need a pristine project without these generated files. This can be done with a Unix find command or through DMP's ``dmp_cleanup`` management command:

.. tabs::

   .. group-tab:: Linux/Mac

        .. code:: bash

            # see what would be be done without actually deleting any cache folders
            python3 manage.py dmp_cleanup --trial-run

            # really delete the folders
            python3 manage.py dmp_cleanup

   .. group-tab:: Windows

        .. code:: powershell

            # see what would be be done without actually deleting any cache folders
            python manage.py dmp_cleanup --trial-run

            # really delete the folders
            python manage.py dmp_cleanup



With this management command, add ``--verbose`` to the command to include messages about skipped files, and add ``--quiet`` to silence all messages (except errors).
