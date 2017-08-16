T2: .py View Files
===================================

.. contents::
    :depth: 2

Let's add some "work" to the process by adding the current server time to the index page. Create a new file ``homepage/views/index.py`` and copy this code into it:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime

    @view_function
    def process_request(request):
        context = {
            'now': datetime.now(),
        }
        return request.dmp_render('index.html', context)

Reload your server and browser page, and you should see the exact same page. It might look the same, but something very important happened in the routing. Rather than going straight to the ``index.html`` page, processing went to your new ``index.py`` file. At the end of the ``process_request`` function above, we manually render the ``index.html`` file. In other words, we're now doing extra "work" before the rendering. This is the place to do database connections, modify objects, prepare and handle forms, etc. It keeps complex code out of your html pages.

Let me pause for a minute and talk about log messages. If you enabled the logger in the installation, you should see the following in your console:

::

    DEBUG::DMP variables set by urls.py: ['dmp_router_app', 'dmp_router_page', 'urlparams']; variables set by defaults: ['dmp_router_function'].
    INFO::DMP processing: app=homepage, page=index, module=homepage.views.index, func=process_request, urlparams=['']
    INFO::DMP calling view function homepage.views.index.process_request
    DEBUG::DMP rendering template /Users/conan/Documents/data/teaching/2017/IS 411-413/fomoproject/homepage/templates/index.html

These debug statements are incredibly helpful in figuring out why pages aren't routing right. If your page didn't load right, you'll probably see why in these statements. In my log above, the first line lists what named parameters were matched in ``urls.py``.

The second line shows the how these named (or defaulted) parameters translated into the app, page, module, and function.

The third line shows the controller found the ``index.py`` view, and it called the ``process_request`` function successfully. This is important -- the ``process_request`` function is the "default" view function. This web-accessible function must be decorated with ``@view_function``.

    This decoration with ``@view_function`` is done for security. If the framework were to allow browsers specify any old function, end users could invoke any function of any module on your system! By requiring the decorator, the framework limits end users to one specifically-named function.

You can have multiple decorators on your function, such as a permissions check and ``view_function``. The order isn't important unless the other decorators don't wrap the function correctly.  If ``@view_function`` is listed first, you won't have to worry.

.. code:: python

    @view_function
    @permission_required('can_vote')
    def process_request(request):
        ...

|

    Later in the tutorial, we'll describe another way to call other functions within your view Even though ``process_request`` is the default function, you can actually have multiple web-accessible functions within a single .py file.

As stated earlier, we explicitly call the Mako renderer at the end of the ``process_request`` function. The context (the third parameter of the call) is a dictionary containing variables to be passed to the template.

Let's use the ``now`` variable in our index.html template:

.. code:: html

    <%inherit file="base.htm" />

    <%block name="content">
        <div class="content">
          <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
          <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
          <p class="server-time">The current server time is ${ now }.</p>
          <p class="browser-time">The current browser time is...</p>
        </div>
    </%block>

The ``${ varname }`` code is Mako syntax and is described more fully on the Mako web site. Right now, it's most important that you see how to send data from the view to the template. If you already know Django templates, it should be familiar.

Reload your web page and ensure the new view is working correctly. You should see the server time printed on the screen. Each time you reload the page, the time changes.


The Render Functions
-------------------------

    This section explains the two render functions included with DMP. If you just want to get things working, skip over this section. You can always come back later for an explanation of how things are put together.

In the example above, we used the ``dmp_render`` function to render our template. It's the DMP equivalent of Django's ``render`` shortcut function. The primary difference between the two functions (other than, obviously, the names) is DMP's function is **coupled to the current app**. In contrast, Django searches for templates in a flat list of directories -- while your apps might have templates in them, Django just searches through them in order. DMP's structure is logically app-based: each of your apps contains a ``templates`` directory, and DMP always searches the *current* app directly. With DMP, there are no worries about template name clashes or finding issues.

At the beginning of each request, DMP's middleware determines the current app (i.e. the first item in the url) and adds two render functions to the request object.  These are available throughout your request, with no imports needed.  As long as you are rendering a template in the request's current app, DMP knows where to find the template file.

DMP provides a second function, ``dmp_render_to_string``. This is nearly the same as ``dmp_render``, but ``dmp_render_to_string`` returns a string rather than an ``HttpResponse`` object. Scroll to `Mime Types and Status Codes`_ to see an example of the ``dmp_render_to_string`` function.

**You really don't need to worry about any of this.**  Templates are rendered in the current app 99% of the time, so just use this code unless you are in a special use case:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime

    @view_function
    def process_request(request):
        context = {
            'now': datetime.now(),
        }
        return request.dmp_render('index.html', context)


Django API Calls
--------------------------------

As a template engine, DMP conforms to the Django standard.  If you need/want to use the standard Django template functions, use the following:

.. code:: python

    from django.shortcuts import render
    return render(request, 'homepage/index.html', context)

or to be more explicit with Django:

.. code:: python

    from django.shortcuts import render
    return render(request, 'homepage/index.html', context, using='django_mako_plus')

Note in the above code that you need to specify the template in the format ``app/template``.  This allows DMP find the right app to load the template from.


Further Reading
---------------------------

The `advanced topic on templates <topics_templates.html>`_ expands with the following topics:

* Templates in other apps
* Templates in other directories, even outside the project
* Controlling content types and HTTP codes
* Convenience functions