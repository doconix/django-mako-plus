T5: Ajax
=========================================

.. contents::
    :depth: 2

What would the modern web be without Ajax?  Truthfully...a lot simpler. :) In fact, if we reinvented the web with today's requirements, we'd probably end up at a very different place than our current web. Even the name ajax implies the use of xml -- which we don't use much in ajax anymore. Most ajax calls return json or html these days!

But regardless of web history, ajax is required on most pages today. I'll assume you understand the basics of ajax and focus specifically on the ways this framework supports it.

A Simple Example
---------------------

Suppose we want to reload the server time every few seconds, but we don't want to reload the entire page. Let's start with the client side of things. Let's place a refresh button in ``homepage/templates/index.html``:

.. code:: html

    <%inherit file="base.htm" />

    <%block name="content">
        <div class="content">
          <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
          <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
          <p class="server-time">The current server time is ${ now }.</p>
          <button id="server-time-button">Refresh Server Time</button>
          <p class="browser-time">The current browser time is .</p>
        </div>
    </%block>

Note the new ``<button>`` element in the above html. Next, we'll add
Javascript to the ``homepage/scripts/index.jsm`` file that runs when the
button is clicked:

.. code:: javascript

    $(function() {
        // update the time every n seconds
        window.setInterval(function() {
            $('.browser-time').text('The current browser time is ' + new Date());
        }, ${ request.dmp.urlparams[1] });

        // update server time button
        $('#server-time-button').click(function() {
            $('.server-time').load('/homepage/index_time/');
        });
    });

The client side is now ready, so let's create the
``/homepage/index_time/`` server endpoint. Create a new
``homepage/views/index_time.py`` file:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime
    import random

    @view_function
    def process_request(request):
        context = {
            'now': datetime.now(),
        }
        return request.render('index_time.html', context)

Finally, create the ``/homepage/templates/index_time.html`` template,
which is rendered at the end of ``process_request()`` above:

.. code:: html

    <%inherit file="base_ajax.htm" />

    <%block name="content">
        The current server time is ${ now }.
    </%block>

Note that this template inherits from ``base_ajax.htm``. If you open ``base_ajax.htm``, you'll see it doesn't have the normal ``<html>``, ``<body>``, etc. tags in it. This supertemplate is meant for snippets of html rather than entire pages. What it **does** contain is the calls to the ``static_renderer`` -- the real reason we inherit rather than just have a standalone template snippet. By calling ``static_renderer`` in the supertemplate, any CSS or JS files are automatically included with our template snippet. Styling the ajax response is as easy as creating a ``homepage/styles/index_time.css`` file.

    We really didn't need to create ``index_time.html`` at all. Just
    like in Django, a view function can simply return an
    ``HttpResponse`` object. At the end of the view function, we simply
    needed to
    ``return HttpResponse('The current server time is %s' % now)``. The
    reason I'm rendering a template here is to show the use of
    ``base_ajax.htm``, which automatically includes .css and .js files
    with the same name as the template.

Reload your browser page and try the button. It should reload the time *from the server* every time you push the button.

    **Hidden powerup alert!** You can also render a partial template by
    specifying one of its ``<%block>`` or ``<%def>`` tags directly in
    ``render()``. See `Rendering Partial
    Templates <#rendering-partial-templates-ajax>`__ for more
    information.

Really, a Whole New File for Ajax?
----------------------------------

All right, there **is** a shortcut, and a good one at that. The last section showed you how to create an ajax endpoint view. Since modern web pages have many little ajax calls thoughout their pages, the framework allows you to put several web-accessible methods **in the same .py file**.

Let's get rid of ``homepage/views/index_time.py``. That's right, just delete the file. Now rename ``homepage/templates/index_time.html`` to ``homepage/templates/index.gettime.html``. This rename of the html file isn't actually necessary, but it's a nice way to keep the view and template names consistent.

Open ``homepage/views/index.py`` and add the following to the end of the
file:

.. code:: python

    @view_function
    def gettime(request):
        context = {
            'now': datetime.now(),
        }
        return request.render('index.gettime.html', context)

Note the function is decorated with ``@view_function``, and it contains the function body from our now-deleted ``index_time.py``. The framework recognizes **any** function with this decorator as an available endpoint for urls, not just the hard-coded ``process_request`` function. In other words, you can actually name your view methods any way you like, as long as you follow the pattern described in this section.

In this case, getting the server time is essentially "part" of the index page, so it makes sense to put the ajax endpoint right in the same file. Both ``process_request`` and ``gettime`` serve content for the ``/homepage/index/`` html page. Having two view files is actually more confusing to a reader of your code because they are so related. Placing two view functions (that are highly related like these are) in the same file keeps everything together and makes your code more concise and easier to understand.

To take advantage of this new function, let's modify the url in
``homepage/scripts/index.jsm``:

.. code:: javascript

    // update button
    $('#server-time-button').click(function() {
        $('.server-time').load('/homepage/index.gettime');
    });

The url now points to ``index.gettime``, which the framework translates to ``index.py -> gettime()``. In other words, a dot (.) gives an exact function within the module to be called rather than the default ``process_request`` function.

Reload your browser page, and the button should still work. Press it a few times and check out the magic.

To repeat, a full DMP url is really ``/app/view.function/``. Using ``/app/view/`` is a shortcut, and the framework translates it as ``/app/view.process_request/`` internally.

    Since ajax calls often return JSON, XML, or simple text, you often
    only need to add a function to your view. At the end of the
    function, simply ``return HttpResponse("json or xml or text")``. You
    likely don't need full template, css, or js files.
