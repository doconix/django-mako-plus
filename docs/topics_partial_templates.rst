Rendering Partial Templates (Ajax!)
======================================

.. contents::
    :depth: 2

One of the hidden easter eggs of Mako is its ability to render individual blocks of a template, and this feature can be used to make reloading parts of a page quick and easy. Are you thinking Ajax here? The trick is done by specifying the ``def_name`` parameters in ``render()``. You may want to start by reading about ``<%block>`` and ``<%def>`` tags in the `Mako documentation <http://docs.makotemplates.org/en/latest/defs.html>`__.

Why Should I Care?
--------------------

**Partial templates rock because:**

1. We serve both the initial page *and* the Ajax call with the same
   code. Write once, debug once, maintain once. Single templates, FTW!
2. The same logic, ``index.py``, is run for both the initial call and
   the Ajax call. While this example is really simplistic, more complex
   views may have significant work to do (form handling, table creation,
   object retrieval) before the page or the Ajax can be rendered.
3. By splitting the template into many different blocks, a single
   view/template can serve many different Ajax calls throughout the
   page.

    Note that, in the Ajax call, your view will likely perform more
    logic than is needed (i.e. generate data for the parts of the
    template outside the block that won't be rendered). Often, this
    additional processing is minimal and is outweighed by the benefits
    above. When additional processing is not desirable, simply create
    new ``@view_function`` functions, one for each Ajax call. You can
    still use the single template by having the Ajax endpoints render
    specific blocks.

An Example
----------------------

Suppose you have the following template, view, and JS files:

**``index.html``** with a ``server_time`` block:

.. code-block:: html+mako

    <%inherit file="base.htm" />

    <%block name="content">
        <div class="content">
          <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
          <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
          <p class="server-time">
              <%block name="server_time">
                 The current server time is ${ now }.
              </%block>
          </p>
          <button id="server-time-button">Refresh Server Time</button>
          <p class="browser-time">The current browser time is .</p>
        </div>
    </%block>

**``index.py``** with an ``if`` statement and two ``request.dmp.render`` calls:

.. code-block:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime
    import random

    @view_function
    def process_request(request):
        context = {
            'now': datetime.now().strftime('%H:%M'),
        }
        if request.dmp.urlparams[0] == 'gettime':
            return request.dmp.render('index.html', context, def_name='server_time')
        return request.dmp.render('index.html', context)

**``index.js``**:

.. code-block:: javascript

    // update button
    $('#server-time-button').click(function() {
        $('.server-time').load('/homepage/index/gettime/');
    });

On initial page load, the ``if request.dmp.urlparams[0] == 'gettime':`` statement is false, so the full ``index.html`` file is rendered. However, when the update button's click event is run, the statement is **true** because ``/gettime`` is added as the first url parameter. This is just one way to switch the ``request.dmp.render`` call. We could also have used a regular CGI parameter, request method (GET or POST), or any other way to perform the logic.

When the ``if`` statement goes **true**, DMP renders the ``server_time`` block of the template instead of the entire template. This corresponds nicely to the way the Ajax call was made: ``$('.server-time').load()``.


Variable Scope
----------------------

The tricky part of block rendering is ensuring your variables are accessible. You can read more about namespaces on the Mako web site, but here's the tl;dr version:

-  Variables sent from the view in the context dictionary are available
   throughout the page, regardless of the block. If your variables are
   part of the context, you're golden.
-  Variables created within your template but **outside the block** have
   to be explicitly defined in the block declaration. This is a Mako
   thing, and it's a consequence of the way Mako turns blocks and defs
   into Python methods. If you need a variable defined outside a block,
   be sure to define your template with a comma-separated list of
   ``args``. Again, `the Mako
   documentation <http://docs.makotemplates.org/en/latest/namespaces.html>`__
   gives more information on these fine details.

**``index.html``** with a ``counter`` variable defined in the template:

.. code-block:: html+mako

    <%inherit file="base.htm" />

    <%block name="content">
        <div class="content">
          <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
          <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
          %for counter in range(10):
              <p class="server-time">
                  <%block name="server_time" args="counter">
                     ${ counter }: The current server time is ${ now }.
                  </%block>
              </p>
          %endfor
          <button id="server-time-button">Refresh Server Time</button>
          <p class="browser-time">The current browser time is .</p>
        </div>
    </%block>

Since ``counter`` won't get defined when ``def_name='server_time'``, **``index.py``** must add it to the ``context`` (but only for the Ajax-oriented ``request.dmp.render`` function):

.. code-block:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from datetime import datetime
    import random

    @view_function
    def process_request(request):
        context = {
            'now': datetime.now().strftime('%H:%M:%S'),
        }
        if request.dmp.urlparams[0] == 'gettime':
            context['counter'] = 100
            return request.dmp.render('index.html', context, def_name='server_time')
        return request.dmp.render('index.html', context)

    The ``def_name`` parameter can be used to call both ``<%block>`` and
    ``<%def>`` tags in your templates. The two are very similar within
    the Mako engine. The primary difference is the ``<%def>`` tag can
    define parameters. When calling these defs directly, be sure each of
    the parameter names is in your ``context`` dictionary.
