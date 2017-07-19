T4: zip(HTML, JS, CSS)
===========================================

.. contents::
    :depth: 2

Modern web pages are made up of three primary parts: HTML, CSS, and Javascript (media might be a fourth, but we'll go with three for now). Since all of your pages need these three components, this framework combines them intelligently for you. All you have to do is name the .html, the css., and the .js files correctly, and DMP will insert the ``<link>`` and ``<script>`` tags automatically for you.

Convention over configuration.  Just like a slice of home-baked apple pie.

A Bit of Style
---------------------------------------------------

To style our index.html file, create ``homepage/styles/index.css`` and copy the following into it:

.. code:: python

    .server-time {
        font-size: 2em;
        color: red;
    }

When you refresh your page, the server time should be styled with large, red text. If you view the html source in your browser, you'll see a new ``<link...>`` near the top of your file. It's as easy as naming the files the same and placing the .css file in the styles/ directory.

The framework knows how to follow template inheritance. For example, since ``index.html`` extends from ``base.htm``, we can actually put our CSS in any of **four** different files: ``index.css``, ``index.cssm``, ``base.css``, and ``base.cssm`` (the .cssm files are explained in the next section). Place your CSS styles in the appropriate file, depending on where the HTML elements are located. For example, let's style our header a little. Since the ``<header>`` element is in ``base.htm``, create ``homepage/styles/base.css`` and place the following in it:

.. code:: css

    html, body {
        margin: 0;
        padding: 0;
    }

    header {
        padding: 36px 0;
        text-align: center;
        font-size: 2.5em;
        color: #F4F4F4;
        background-color: #0088CC;
    }

Reload your browser, and you should have a nice white on blue header. If you view source in the browser, you'll see the CSS files were included as follows:

.. code:: html

    <link rel="stylesheet" type="text/css" href="/static/homepage/styles/base.css?33192040" />
    <link rel="stylesheet" type="text/css" href="/static/homepage/styles/index.css?33192040" />

Note that ``base.css`` is included first because it's at the top of the hierarchy. Styles from ``index.css`` override any conflicting styles from ``base.css``, which makes sense because ``index.html`` is the final template in the inheritance chain.

    You might be wondering about the big number after the html source ``<link>``. That's the file modification time, in minutes since 1970. This is included because browsers (especially Chrome) don't automatically download new CSS files. They use their cached versions until a specified date, often far in the future (this duration is set by your web server). By adding a number to the end of the file, browsers think the CSS files are "new" because the "filename" changes whenever you change the file. Trixy browserses...

A Bit of Style, Reloaded
------------------------

The style of a web page is often dependent upon the user, such as a user-definable theme in an online email app or a user-settable font family in an online reader. DMP supports this behavior, mostly because the authors at MyEducator needed it for their online book reader. You can use Mako (hence, any Python code) not only in your .html files, but also in your CSS files. Simply name the file with ``.cssm`` rather than .css. When the framework sees ``index.cssm``, it runs the file through the Mako templating engine before it sends it out.

    Since .cssm files are generated per request, they are embedded directly in the HTML rather than linked. This circumvents a second call to the server, which would happen every time since the CSS is being dynamically generated. Dynamic CSS can't be cached by a browser any more than dynamic HTML can.

Let's make the color dynamic by adding a new random variable ``timecolor`` to our index.py view:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from .. import dmp_render, dmp_render_to_string
    from datetime import datetime
    import random

    @view_function
    def process_request(request):
        context = {
            'now': datetime.now().strftime(request.urlparams[0] if request.urlparams[0] else '%H:%M'),
            'timecolor': random.choice([ 'red', 'blue', 'green', 'brown' ]),
        }
        return dmp_render(request, 'index.html', context)

Now, rename your index.css file to ``index.cssm``. Then set the content of index.cssm to the following:

.. code:: css

    .server-time {
        font-size: 2em;
        color: ${ timecolor };
    }

Refresh your browser a few times. Hey look, Ma, the color changes with each refresh!

As shown in the example above, the context dictionary sent the templating engine in ``process_request`` are globally available in .html, .cssm, and .jsm files.

    Note that this behavior is different than CSS engines like Less and Sass. Most developers use Less and Sass for variables at development time. These variables are rendered and stripped out before upload to the server, and they become static, normal CSS files on the server. .cssm files should be used for dynamically-generated, per-request CSS.

Static and Dynamic Javascript
-----------------------------

Javascript files work the same way as CSS files, so if you skipped the two CSS sections above, you might want to go read through them. This section will be more brief because it's the same pattern again. Javascript files are placed in the ``scripts/`` directory, and both static ``.js`` files and dynamically-created ``.jsm`` files are supported.

Let's add a client-side, Javascript-based timer. Create the file ``homepage/scripts/index.js`` and place the following JQuery code into it:

.. code:: javascript

    $(function() {
        // update the time every 1 seconds
        window.setInterval(function() {
            $('.browser-time').text('The current browser time is ' + new Date() + '.');
        }, 1000);
    });

Refresh your browser page, and you should see the browser time updating each second. Congratulations, you've now got a modern, HTML5 web page.

Let's also do an example of a ``.jsm`` (dynamic) script. We'll let the user set the browser time update period through a urlparam. We'll leave the first parameter alone (the server date format) and use the second parameter to specify this interval.

First, **be sure to change the name of the file from ``index.js`` to ``index.jsm``.** This tells the framework to run the code through the Mako engine before sending to the browser. In fact, if you try leaving the .js extension on the file and view the browser source, you'll see the ``${ }`` Mako code doesn't get rendered. It just gets included like static html. Changing the extension to .jsm causes DMP to run Mako and render the code sections.

Update your ``homepage/scripts/index.jsm`` file to the following:

.. code:: javascript

    $(function() {
        // update the time every 1 seconds
        window.setInterval(function() {
            $('.browser-time').text('The current browser time is ' + new Date() + '.');
        }, ${ request.urlparams[1] });
    });

Save the changes and take your browser to `http://localhost:8000/homepage/index/%Y/3000/ <http://localhost:8000/homepage/index/%Y/3000/>`__. Since urlparams[1] is 3000 in this link, you should see the date change every three seconds. Feel free to try different intervals, but out of concern for the innocent (e.g. your browser), I'd suggest keeping the interval above 200 ms.

    I should note that letting the user set date formats and timer intervals via the browser url are probably not the most wise or secure ideas. But hopefully, it is illustrative of the capabilities of DMP.

Minification of JS and CSS
--------------------------

DMP will try to minify your \*.js and \*.css files using the ``rjsmin`` and ``rcssmin`` modules if the settings.py ``MINIFY_JS_CSS`` is True. Your Python installation must also have these modules installed.

These two modules do fairly simplistic minification using regular expressions. They are not as full-featured as other minifiers, but they use pure Python code and are incredibly fast. If you want more complete minification, this probably isn't it.

These two modules might be simplistic, but they *are* fast enough to do minification of dynamic ``*.jsm`` and ``*.cssm`` files at production time. Setting the ``MINIFY_JS_CSS`` variable to True will not only minify during the ``dmp_collectstatic`` command, it will minfiy the dynamic files as well as they are rendered for each client.

I've done some informal speed testing with dynamic scripts and styles, and minification doesn't really affect overall template processing speed. YMMV. Luck favors those that do their own testing.

Again, if you want to disable these minifications procedures, simply set ``MINIFY_JS_CSS`` to False.

Minification of ``*.jsm`` and ``*.cssm`` is skipped during development so you can debug your Javascript and CSS. Even if your set ``MINIFY_JS_CSS`` to True, minification only happens when settings.py ``DEBUG`` is False (at production).


Behind the CSS and JS Curtain
-----------------------------

After reading about automatic CSS and JS inclusion, you might want to know how it works. It's all done in the templates (base.htm now, and base\_ajax.htm in a later section below) you are inheriting from. Open ``base.htm`` and look at the following code:

::

    ## render the styles with the same name as this template and its supertemplates
    ${ django_mako_plus.link_css(self) }

    ...

    ## render the scripts with the same name as this template and its supertemplates
    ${ django_mako_plus.link_js(self) }

The two calls, ``link_css()`` and ``link_js()``, include the ``<link>`` and ``<script>`` tags for the template name and all of its supertemplates. The CSS should be linked near the top of your file (``<head>`` section), and the JS should be linked near the end (per best practices).

This all works because the ``index.html`` template extends from the ``base.htm`` template. If you fail to inherit from ``base.htm`` or ``base_ajax.htm``, DMP won't be able to include the support files.

