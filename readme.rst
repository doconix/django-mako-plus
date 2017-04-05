











Importing Python Modules into Templates
---------------------------------------

It's easy to import Python modules into your Mako templates. Simply use a module-level block:

.. code:: python

    <%!
        import datetime
        from decimal import Decimal
    %>

or a Python-level block (see the Mako docs for the difference):

.. code:: python

    <%
        import datetime
        from decimal import Decimal
    %>

There may be some modules, such as ``re`` or ``decimal`` that are so useful you want them available in every template of your site. In settings.py, add these to the ``DEFAULT_TEMPLATE_IMPORTS`` variable:

.. code:: python

    DEFAULT_TEMPLATE_IMPORTS = [
        'import os, os.path, re',
        'from decimal import Decimal',
    ],

Any entries in this list will be automatically included in templates throughout all apps of your site. With the above imports, you'll be able to use ``re`` and ``Decimal`` and ``os`` and ``os.path`` anywhere in any .html, .cssm, and .jsm file.

    Whenever you modify the DMP settings, be sure to clean out your
    cached templates with ``python manage.py dmp_cleanup``. This ensures
    your compiled templates are rebuilt with the new settings.

Mime Types and Status Codes
---------------------------

The ``dmp_render()`` function determines the mime type from the template extension and returns a *200* status code. What if you need to return JSON, CSV, or a 404 not found? Just wrap the ``dmp_render_to_string`` function in a standard Django ``HttpResponse`` object. A few examples:

.. code:: python

    from django.http import HttpResponse

    # return CSV
    return HttpResponse(dmp_render_to_string(request, 'my_csv.html', {}), mimetype='text/csv')

    # return a custom error page
    return HttpResponse(dmp_render_to_string(request, 'custom_error_page.html', {}), status=404)

Static Files, Your Web Server, and DMP
--------------------------------------

Static files are files linked into your html documents like ``.css`` and ``.js`` as well as images files like ``.png`` and ``.jpg``. These are served directly by your web server (Apache, Nginx, etc.) rather than by Django because they don't require any processing. They are just copied across the Internet. Serving static files is what web servers were written for, and they are better at it than anything else.

Django-Mako-Plus works with static files the same way that traditional Django does, with one difference: the folder structure is different in DMP. The folllowing subsections describe how you should use static files with DMP.

    If you read nothing else in this tutorial, be sure to read through
    the Deployment subsection given shortly. There's a potential
    security issue with static files that you need to address before
    deploying. Specifically, you need to comment out ``BASE_DIR`` from
    the setup shown next.

Static File Setup
^^^^^^^^^^^^^^^^^

In your project's settings.py file, be sure you add the following:

.. code:: python

    STATIC_URL = '/static/'
    STATICFILES_DIRS = (
        BASE_DIR,
    )
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

Note that the last line is a serious security issue if you go to production with it (although Django disables it as long as ``DEBUG=False``). More on that later.

Development
^^^^^^^^^^^

During development, Django will use the ``STATICFILES_DIRS`` variable to find the files relative to your project root. You really don't need to do anything special except ensure that the ``django.contrib.staticfiles`` app is in your list of ``INSTALLED_APPS``. Django's ``staticfiles`` app is the engine that statics files during development.

Simply place media files for the homepage app in the homepage/media/ folder. This includes images, videos, PDF files, etc. -- any static files that aren't Javascript or CSS files.

Reference static files using the ``${ STATIC_URL }`` variable. For example, reference images in your html pages like this:

.. code:: html

    <img src="${ STATIC_URL }homepage/media/image.png" />

By using the ``STATIC_URL`` variable from settings in your urls rather than hard-coding the ``/static/`` directory location, you can change the url to your static files easily in the future.

Security at Deployment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At production/deployment, comment out ``BASE_DIR`` because it essentially makes your entire project available via your static url (a serious security concern):

.. code:: python

    STATIC_URL = '/static/'
    STATICFILES_DIRS = (
        # BASE_DIR,
    )
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

When you deploy to a web server, run ``dmp_collectstatic`` to collect your static files into a separate directory (called ``/static/`` in the settings above). You should then point your web server (Apache, Nginx, IIS, etc.) to serve this folder directly to browsers. For example, in Nginx, you'd set the following:

::

    location /static/ {
        alias /path/to/your/project/static/;
        access_log off;
        expires 30d;
    }

In Apache, you'd set the following:

Alias /static/ /path/to/your/project/static/

::

    <Directory /path/to/your/project/static/>
    Order deny,allow
    Allow from all
    </Directory>

Collecting Static Files
^^^^^^^^^^^^^^^^^^^^^^^

DMP comes with a management command called ``dmp_collectstatic`` that copies all your static resource files into a single subtree so you can easily place them on your web server. At development, your static files reside within the apps they support. For example, the ``homepage/media`` directory is a sibling to ``homepage/views`` and ``/homepage/templates``. This combined layout makes for nice development, but a split layout is more optimal for deployment because you have two web servers active at deployment (a traditional server like Apache doing the static files and a Python server doing the dynamic files).

A Django-Mako-Plus app has a different layout than a traditional Django app, so it comes with its own static collection command. When you are ready to publish your web site, run the following to split out the static files into a single subtree:

.. code:: python

    python3 manage.py dmp_collectstatic

This command will copy the static directories--\ ``/media/``, ``/scripts/``, and ``/styles/``--to a common subtree called ``/static/`` (or whatever ``STATIC_ROOT`` is set to in your settings). Everything in these directories is copied (except dynamic ``*.jsm/*.cssm`` files, which aren't static).

    The command copies only these three directorie out of your DMP app
    folders. Any other directories, such as ``views`` and ``templates``
    and ``mydir`` are skipped. If you need to include additional
    directories or file patterns, use the option below.

The ``dmp_collectstatic`` command has the following command-line options:

-  The commmand will refuse to overwrite an existing ``/static/``
   directory. If you already have this directory (either from an earlier
   run or for another purpose), you can 1) delete it before collecting
   static files, or 2) specify the overwrite option as follows:

::

    python3 manage.py dmp_collectstatic --overwrite

-  If you need to ignore certain directories or filenames, specify them
   with the ``--skip-dir`` and ``--skip-file`` options. These can be
   specified more than once, and it accepts Unix-style wildcards.

::

    python3 manage.py dmp_collectstatic --skip-dir=.cached_templates --skip-file=*.txt --skip-file=*.md

-  If you need to include additional directories or files, specify them
   with the ``--include`` option. This can be specified more than once,
   and it accepts Unix-style wildcards:

::

    python3 manage.py dmp_collectstatic --include-dir=global-media --include-dir=global-styles --include-file=*.png

Django Apps + DMP Apps
''''''''''''''''''''''

You might have some traditional Django apps (like the built-in ``/admin`` app) and some DMP apps (like our ``/homepage`` in this tutorial). Your Django apps need the regular ``collectstatic`` routine, and your DMP apps need the ``dmp_collectstatic`` routine.

The solution is to run both commands. Using the options of the two commands, you can either send the output from each command to *two different* static directories, or you can send them to a single directory and let the files from the second command potentially overwrite the files from the first. I suggest this second method:

::

    python3 manage.py collectstatic
    python3 manage.py dmp_collectstatic --overwrite

The above two commands will use both methods to bring files into your ``/static/`` folder. You might get some duplication of files, but the output of the commands are different enough that it should work without issues.

Redirecting
-----------

Redirecting the browser is common in today's sites. For example, during form submissions, web applications often redirect the browser to the *same* page after a form submission (and handling with a view)--effectively switching the browser from its current POST to a regular GET. If the user hits the refresh button within his or her browser, the page simply gets refreshed without the form being submitted again. It prevents users from being confused when the browser opens a popup asking if the post data should be submitted again.

DMP provides a Javascript-based redirect response and four exception-based redirects. The first, ``HttpResponseJavascriptRedirect``, sends a regular HTTP 200 OK response that contains Javascript to redirect the browser: ``<script>window.location.href="...";</script>``. Normally, redirecting should be done via Django's built-in ``HttpResponseRedirect`` (HTTP 302), but there are times when a normal 302 doesn't do what you need. For example, suppose you need to redirect the top-level page from an Ajax response. Ajax redirects normally only redirects the Ajax itself (not the page that initiated the call), and this default behavior is usually what is needed. However, there are instances when the entire page must be redirected, even if the call is Ajax-based. Note that this class doesn't use the tag or Refresh header method because they aren't predictable within Ajax (for example, JQuery seems to ignore them).

The four exception-based redirects allow you to raise a redirect from anywhere in your code. For example, the user might not be authenticated correctly, but the code that checks for this can't return a response object. Since these three are exceptions, they bubble all the way up the call stack to the DMP router -- where they generate a redirect to the browser. Exception-based redirects should be used sparingly, but they can help you create clean code. For example, without the ability to redirect with an exception, you might have to pass and return other variables (often the request/response objects) through many more function calls.

As you might expect, ``RedirectException`` sends a normal 302 redirect and ``PermanentRedirectException`` sends a permanent 301 redirect. ``JavascriptRedirectException`` sends a redirect ``HttpResponseJavascriptRedirect`` as described above.

The fourth exception, ``InternalRedirectException``, is simpler and faster: it restarts the routing process with a different view/template within the *current* request, without changing the browser url. Internal redirect exceptions are rare and shouldn't be abused. An example might be returning an "upgrade your browser" page to a client; since the user has an old browser, a regular 302 redirect might not work the way you expect. Redirecting internally is much safer because your server stays in control the entire time.

The following code shows examples of different redirection methods:

.. code:: python

    from django.http import HttpResponseRedirect
    from django_mako_plus import HttpResponseJavascriptRedirect
    from django_mako_plus import RedirectException, PermanentRedirectException, JavascriptRedirectException, InternalRedirectException

    # return a normal redirect with Django from a process_request method
    return HttpResponseRedirect('/some/new/url/')

    # return a Javascript-based redirect from a process_request method
    return HttpResponseJavascriptRedirect('/some/new/url/')

    # raise a normal redirect from anywhere in your code
    raise RedirectException('/some/new/url')

    # raise a permanent redirect from anywhere in your code
    raise PermanentRedirectException('/some/new/url')

    # raise a Javascript-based redirect from anywhere in your code
    raise JavascriptRedirectException('/some/new/url')

    # restart the routing process with a new view without returning to the browser.
    # the browser keeps the same url and doesn't know a redirect has happened.
    # the request.dmp_router_module and request.dmp_router_function variables are updated
    # to reflect the new values, but all other variables, such as request.urlparams,
    # request.GET, and request.POST remain the same as before.
    # the next line is as if the browser went to /homepage/upgrade/
    raise InternalRedirectException('homepage.views.upgrade', 'process_request')

DMP adds a custom header, "Redirect-Exception", to all exception-based redirects. Although you'll probably ignore this most of the time, the header allows you to further act on exception redirects in response middleware, your web server, or calling Javascript code.

    Is this an abuse of exceptions? Probably. But from one viewpoint, a
    redirect can be seen as an exception to normal processing. It is
    quite handy to be able to redirect the browser from anywhere in your
    codebase. If this feels dirty to you, feel free to skip it.

Deployment Recommendations
==========================

This section has nothing to do with the Django-Mako-Framework, but I want to address a couple issues in hopes that it will save you some headaches. One of the most difficult decisions in Django development is deciding how to deploy your system. In particular, there are several ways to connect Django to your web server: mod\_wsgi, FastCGI, etc.

At MyEducator, we've been through all of them at various levels of testing and production. By far, we've had the best success with `uWSGI <http://docs.djangoproject.com/en/dev/howto/deployment/wsgi/uwsgi/>`__. It is a professional server, and it is stable.

One other decision you'll have to make is which database use. I'm excluding the "big and beefies" like Oracle or DB2. Those with sites that need these databases already know who they are. Most of you will be choosing between MySQL, PostgreSQL, and perhaps another mid-level database.

In choosing databases, you'll find that many, if not most, of the Django developers use PostgreSQL. The system is likely tested best and first on PG. We started on MySQL, and we moved to PG after experiencing a few problems. Since deploying on PG, things have been amazingly smooth.

Your mileage may vary with everything in this section. Do your own testing and take it all as advice only. Best of luck.

Deployment Tutorials
--------------------

The following links contain tutorials for deploying Django with DMP:

-  http://blog.tworivershosting.com/2014/11/ubuntu-server-setup-for-django-mako-plus.html

Advanced Topics
===============

The following sections are for those who want to take advantage of some extra, but likely less used, features of DMP.

Useful Variables
----------------

At the beginning of each request (as part of its middleware), DMP adds a number of fields to the request object. These variables primarily support the inner workings of the DMP router, but they may be useful to you as well. The following are available throughout the request:

-  ``request.dmp_router_app``: The Django application specified in the
   URL. In the URL ``http://www.server.com/calculator/index/1/2/3``, the
   ``dmp_router_app`` is the string "calculator".
-  ``request.dmp_router_page``: The name of the Python module specified
   in the URL. In the URL
   ``http://www.server.com/calculator/index/1/2/3``, the
   ``dmp_router_page`` is the string "index". In the URL
   ``http://www.server.com/calculator/index.somefunc/1/2/3``, the
   ``dmp_router_page`` is still the string "index".
-  ``request.dmp_router_function``: The name of the function within the
   module that will be called, even if it is not specified in the URL.
   In the URL ``http://www.server.com/calculator/index/1/2/3``, the
   ``dmp_router_function`` is the string "process\_request" (the default
   function). In the URL
   ``http://www.server.com/calculator/index.somefunc/1/2/3``, the
   ``dmp_router_page`` is the string "somefunc".
-  ``request.dmp_router_module``: The name of the real Python module
   specified in the URL, as it will be imported into the runtime module
   space. In the URL ``http://www.server.com/calculator/index/1/2/3``,
   the ``dmp_router_module`` is the string "calculator.views.index".
-  ``request.dmp_router_class``: The name of the class if the router
   sees that the "function" is actually a class-based view. None
   otherwise.
-  ``request.urlparams``: A list of parameters specified in the URL. See
   the section entitled "URL Parameters" above for more information.

Custo\_dmp\_router\_callablen
-----------------------------

Suppose your project requires a different URL pattern than the normal ``/app/page/param1/param2/...``. For example, you might need the user id in between the app and page: ``/app/userid/page/param1/param1...``. This is supported in two different ways.

URL Patterns: Take 1
^^^^^^^^^^^^^^^^^^^^

The first method is done with named parameters, and it is the "normal" way to customize the url pattern. Instead of including the default\ ``django_mako_plus.urls`` module in your ``urls.py`` file, you can instead create the patterns manually. Start with the `patterns in the DMP source <http://github.com/doconix/django-mako-plus/blob/master/django_mako_plus/urls.py>`__ and modify them as needed.

The following is one of the URL patterns, modified to include the ``userid`` parameter in between the app and page:

::

    from django_mako_plus import route_request
    urlpatterns = [
        ...
        url(r'^(?P<dmp_router_app>[_a-zA-Z0-9\.\-]+)/(?P<userid>\d+)/(?P<dmp_router_page>[_a-zA-Z0-9\.\-]+)/?(?P<urlparams>.*)$', route_request, name='DMP - /app/page'),
        ...
    ]

Then, in your process\_request method, be sure to include the userid parameter. This is according to the standard Django documentation with named parameters:

::

    @view_function
    def process_request(request, userid):
        ...

DMP doesn't use the positional index of the arguments, so you can rearrange patterns as needed. However, you must use named parameters for both DMP and your custom parameters (Django doesn't allow both named and positional parameters in a single pattern).

You can also "hard code" the app or page name in a given pattern. Suppose you want URLs entirely made of numbers (without any slashes) to go the user app: ``/user/views/account.py``. The pattern would hard-code the app and page as `extra options <http://docs.djangoproject.com/en/1.10/topics/http/urls/#passing-extra-options-to-view-functions>`__. In urls.py:

.. code:: python

    from django_mako_plus import route_request
    urlpatterns = [
        ...
        url(r'^(?P<user_id>\d+)$', route_request, { 'dmp_router_app': 'user', 'dmp_router_page': 'account' }, name='User Account'),
        ...
    ]

Use the following named parameters in your patterns to tell DMP which
app, page, and function to call:

-  ``(?P<dmp_router_app>[_a-zA-Z0-9\-]+)`` is the app name. If omitted,
   it is set to ``DEFAULT_APP`` in settings.
-  ``(?P<dmp_router_page>[_a-zA-Z0-9\-]+)`` is the view module name. If
   omitted, it is set to ``DEFAULT_APP`` in settings.
-  ``(?P<dmp_router_function>[_a-zA-Z0-9\.\-]+)`` is the function name.
   If omitted, it is set to ``process_request``.
-  ``(?P<urlparams>.*)`` is the url parameters, and it should normally
   span multiple slashes. The default patterns set this value to
   anything after the page name. This value is split on the slash ``/``
   to form the ``request.urlparams`` list. If omitted, it is set to the
   empty list ``[]``.

The following URL pattern can be used to embed an object ID parameter
(named 'id' in this case) into DMP's conventional URL pattern (between
the app name and the page name):

::

    url(r'^(?P<dmp_router_app>[_a-zA-Z0-9\-]+)/(?P<id>\d+)/(?P<dmp_router_page>[_a-zA-Z0-9\-]+)\.?(?P<dmp_router_function>[_a-zA-Z0-9\-]+)?/?(?P<urlparams>.*)$', route_request, name='/app/id/page(.function)(/urlparams)'),

URL Patterns: Take 2
^^^^^^^^^^^^^^^^^^^^

The second method is done by directly modifying the variables created in the middleware. This can be done through a custom middleware view function that runs after ``django_mako_plus.RequestInitMiddleware`` (or alternatively, you could create an extension to this class and replace the class in the ``MIDDLEWARE`` list).

Once ``RequestInitMiddleware.process_view`` creates the variables, your custom middleware can modify them in any way. As view middleware, your function will run *after* the DMP middleware by *before* routing takes place in ``route_request``.

This method of modifying the URL pattern allows total freedom since you can use python code directly. However, it would probably be done in an exceptional rather than typical case.

CSRF Tokens
-----------

In support of the Django CSRF capability, DMP includes ``csrf_token`` and ``csrf_input`` in the context of every template. Following `Django's lead <https://docs.djangoproject.com/en/dev/ref/csrf/>`__, this token is always available and cannot be disabled for security reasons.

However, slightly different than Django's default templates (but following `Jinja2's lead <https://docs.djangoproject.com/en/dev/ref/csrf/#using-csrf-in-jinja2-templates>`__), use ``csrf_input`` to render the CSRF input:

::

    <form action="" method="post">
        ${ csrf_input }
        ...
    </form>

    Since the CSRF token requires a request object, using an empty
    request ``dmp_render(None, ...)`` prevents the token from being
    included in your templates.

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

Using Django and Jinja2 Tags and Syntax
---------------------------------------

In most cases, third-party functionality can be called directly from Mako. For example, use the `Django Paypal <http://django-paypal.readthedocs.io/>`__ form by converting the Django syntax to Mako:

-  The docs show: ``{{ form.render }}``
-  You use:\ ``${ form.render() }``

In other words, use regular Python in DMP to call the tags and functions within the third party library. For example, you can render a `Crispy Form <http://django-crispy-forms.readthedocs.io/>`__ by importing and calling its ``render_crispy_form`` function right within your template.

For example, suppose your view constructs a Django form, which is then sent to your template via the context dictionary. Your template would look like this:

::

    <%! from crispy_forms.utils import render_crispy_form %>

    <html>
    <body>
        <form method="POST">
            ${ csrf_input }
            ${ render_crispy_form(form) }
        </form>
    </body>
    </html>

If you call the ``render_crispy_form`` method in many templates, you may want to add the import to ``DEFAULT_TEMPLATE_IMPORTS`` in your ``settings.py`` file. Once this import exists in your settings, the function will be globally available in every template on your site.

    Whenever you modify the DMP settings, be sure to clean out your
    cached templates with ``python manage.py dmp_cleanup``. This ensures
    your compiled templates are rebuilt with the new settings.

However, there may be times when you need or want to call real, Django tags. For example, although `Crispy Forms' <http://django-crispy-forms.readthedocs.io/>`__ functions can be called directly, you may want to use its custom tags.

To enable alternative syntaxes, uncomment (or add) the following to your ``settings.py`` file:

.. code:: python

    'DEFAULT_TEMPLATE_IMPORTS': [
        'from django_mako_plus import django_syntax, jinja2_syntax, alternate_syntax
    ],

Then clear out the compiled templates caches:

::

    python manage.py dmp_cleanup

Now that the functions are imported, you can include a Django expression or embed an entire block within your Mako template by using a filter:

::

    ## Expression containing Django template syntax (assuming name was created in the view.py)
    ${ '{{ name }}' | django_syntax(self) }

    ## Full Django code block, with Mako creating the variable first
    <% titles = [ 'First', 'Second', 'Third' ] %>
    <%block filter="django_syntax(self, titles=titles)">
        {% for title in titles %}
            <h2>
                {{ title|upper }}
            </h2>
        {% endfor %}
    </%block>

    ## Third-party, crispy form tags (assume my_formset was created in the view.py)
    <%block filter="django_syntax(self)">
        {% load crispy_forms_tags %}
        <form method="post" class="uniForm">
            {{ my_formset|crispy }}
        </form>
    </%block>

The ``self`` parameter passes your context variables to the Django render call. It is a global Mako variable (available in any template), and it is always included in the filter. In other words, include ``self`` every time as shown in the examples above.

Jinja2, Mustache, Cheetah, and ((insert template engine)).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If Jinja2 is needed, replace the filter with ``jinja2_syntax(context)`` in the above examples. If another engine is needed, replace the filter with ``template_syntax(context, 'engine name')`` as specified in ``settings.TEMPLATES``. DMP will render with the appriate engine and put the result in your HTML page.

Local Variables
^^^^^^^^^^^^^^^

Embedded template code has access to any variable passed to your temple (i.e. any variable in the context). Although not an encouraged practice, variables are sometimes created right in your template, and faithful to the Mako way, are not accessible in embedded blocks.

You can pass locally-created variables as kwargs in the filter call. This is done with ``titles=titles`` in the Django code block example above.

Rendering Mako without DMP Routing
----------------------------------

Just want to render Mako templates within your existing Django project? Want to skip the DMP autorouter and go with the standard ``urls.py`` method? The DMP engine can be used easily with existing Django projects--with very little modification.

The following lists the minimal steps to get DMP running with an existing Django project:

**Create (or open) a standard Django project**:

::

    # install dependencies
    pip3 install django mako django-mako-plus

    # start your project
    python3 -m django startproject tester
    cd tester
    python3 manage.py startapp homepage

    # in tester/settings.py:
    INSTALLED_APPS = [
        # at end of existing list:
        'homepage',
    ]

    # in tester/urls.py:
    import homepage.views
    urlpatterns = [
        # at end of existing list:
        url(r'^$', homepage.views.index, name='index'),
    ]

    # in homepage/views.py:
    from django.shortcuts import render
    from django.http import HttpResponse
    def index(request):
        return HttpResponse("Hello, world. You're at the homepage index.")

    # tested to ensure working
    python3 manage.py runserver
    # browser to http://localhost:8000 (you should see the Hello World response)

**Add a Django template**

::

    # in homepage/templates/homepage/index.html:
    Hello, world. One plus one is ${ 1+1 }.

    # in homepage/views.py:
    from django.template import loader
    from django.http import HttpResponse
    def index(request):
        template = loader.get_template('homepage/index.html')
        return HttpResponse(template.render({}, request))

    # tested to ensure working
    python3 manage.py runserver
    # browser to http://localhost:8000 (you should see the page,
    # but ${ 1+1 } won't render yet because we haven't
    # enabled Mako)

**Add DMP-specific settings to enable Mako**

1. Follow the `DMP directions for your ``settings.py``
   file <#edit-your-settingspy-file>`__ at the top of this document.

   1. Add ``django_mako_plus`` to your INSTALLED\_APPS.
   2. Add ``django_mako_plus.RequestInitMiddleware`` to your MIDDLEWARE.
   3. Add the DMP template engine to your TEMPLATES.

2. Modify your views with the app-based location of your templates:

::

    from django.shortcuts import render

    def index(request):
        context = {}
        return render(request, 'homepage/homepage/index.html', context)

Location, Location, Location...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One subtle, but very important, change in DMP is the **location of your templates**. In the above code, homepage is listed twice because the first specifies the app to use, and the second specfies the subdirectory within ``app/templates/``.

This is because *Django's concept of "template finding" through a number of app and other directories doesn't exist in DMP.* Instead, DMP templates are app-aware; if you were using the DMP-specific functions, like ``dmp_render()``, you wouldn't even need to specify the app. However, since this section is about minimal changes, we're using the standard Django functions.

If you don't like the double-homepage whammy (and I would agree), move your template files up one directory. The following two cases show the options:

::

    # Option 1: your template is located in Django-standard:
    # homepage/templates/homepage/index.html:

    from django.template import loader
    from django.http import HttpResponse

    def index(request):
        # Django code would be:
        template = loader.get_template('homepage/index.html')
        return HttpResponse(template.render(context, request))

        # DMP code would be (first homepage is the app name):
        template = loader.get_template('homepage/homepage/index.html')
        return HttpResponse(template.render(context, request))

::

    # Option 2: your template is located in DMP-standard:
    # homepage/templates/index.html:

    from django.template import loader
    from django.http import HttpResponse

    def index(request):
        # Django code wouldn't find it here (without special finders defined)

        # DMP code would be (first homepage is the app name):
        template = loader.get_template('homepage/index.html')
        return HttpResponse(template.render(context, request))

Rendering Partial Templates (Ajax!)
-----------------------------------

One of the hidden features of Mako is its ability to render individual blocks of a template, and this feature can be used to make reloading parts of a page quick and easy. Are you thinking Ajax here? The trick is done by specifying the ``def_name`` parameters in ``render()``. You may want to start by reading about ``<%block>`` and ``<%def>`` tags in the `Mako documentation <http://docs.makotemplates.org/en/latest/defs.html>`__.

Suppose you have the following template, view, and JS files:

**``index.html``** with a ``server_time`` block:

.. code:: html

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

**``index.py``** with an ``if`` statement and two ``dmp_render`` calls:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from .. import dmp_render, dmp_render_to_string
    from datetime import datetime
    import random

    @view_function
    def process_request(request):
        context = {
            'now': datetime.now().strftime('%H:%M'),
        }
        if request.urlparams[0] == 'gettime':
            return dmp_render(request, 'index.html', context, def_name='server_time')
        return dmp_render(request, 'index.html', context)

**``index.js``**:

.. code:: javascript

    // update button
    $('#server-time-button').click(function() {
        $('.server-time').load('/homepage/index/gettime/');
    });

On initial page load, the ``if request.urlparams[0] == 'gettime':`` statement is false, so the full ``index.html`` file is rendered. However, when the update button's click event is run, the statement is **true** because ``/gettime`` is added as the first url parameter. This is just one way to switch the ``dmp_render`` call. We could also have used a regular CGI parameter, request method (GET or POST), or any other way to perform the logic.

When the ``if`` statement goes **true**, DMP renders the ``server_time`` block of the template instead of the entire template. This corresponds nicely to the way the Ajax call was made: ``$('.server-time').load()``.

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

**Variable Scope**

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

.. code:: html

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

Since ``counter`` won't get defined when ``def_name='server_time'``, **``index.py``** must add it to the ``context`` (but only for the Ajax-oriented ``dmp_render`` function):

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from .. import dmp_render, dmp_render_to_string
    from datetime import datetime
    import random

    @view_function
    def process_request(request):
        context = {
            'now': datetime.now().strftime('%H:%M:%S'),
        }
        if request.urlparams[0] == 'gettime':
            context['counter'] = 100
            return dmp_render(request, 'index.html', context, def_name='server_time')
        return dmp_render(request, 'index.html', context)

    The ``def_name`` parameter can be used to call both ``<%block>`` and
    ``<%def>`` tags in your templates. The two are very similar within
    the Mako engine. The primary difference is the ``<%def>`` tag can
    define parameters. When calling these defs directly, be sure each of
    the parameter names is in your ``context`` dictionary.

Sass Integration
----------------

DMP can automatically compile your .scss files each time you update them. When a template is rendered the first time, DMP checks the timestamps on the .scss file and .css file, and it reruns Sass when necessary. Just be sure to set the ``SCSS_BINARY`` option in settings.py.

When ``DEBUG = True``, DMP checks the timestamps every time a template is rendered. When in production mode (``DEBUG = False``), DMP only checks the timestamps the
first time a template is rendered -- you'll have to restart your server to recompile updated .scss files. You can disable Sass integration by removing the
``SCSS_BINARY`` from the settings or by setting it to ``None``.

Note that ``SCSS_BINARY`` *must be specified in a list*. DMP uses Python's subprocess.Popen command without the shell option (it's more cross-platform that way, and it
works better with spaces in your paths). Specify any arguments in the list as well. For example, the following settings are all valid:

::

    'SCSS_BINARY': [ 'scss' ],
    # or:
    'SCSS_BINARY': [ 'C:\\Ruby200-x64\\bin\\scss' ],
    # or:
    'SCSS_BINARY': [ '/usr/bin/env', 'scss', '--unix-newlines', '--cache-location', '/tmp/' ],
    # or, to disable:
    'SCSS_BINARY': None,

If Sass isn't running right, check the DMP log statements. When the log is enabled, it shows the exact command syntax that DMP is using. Copy and paste the code into a
terminal and troubleshoot the command manually.

    You might be wondering if DMP supports ``.scssm`` files (Mako
    embedded in Sass files). Through a bit of hacking the process, it's
    a qualified Yes! Consider ``.scssm`` support as beta right now. Only
    Mako expressions are working thus far: ``${ ... }``. Any other Mako
    constructs get stripped out by the compiler.

Class-Based Views
-----------------

Django-Mako-Plus supports Django's class-based view concept. You can read more about this pattern in the Django documentation. If you are using view classes, DMP automatically detects and adjusts accordingly. If you are using regular function-based views, skip this section for now.

With DMP, your class-based view will be discovered via request url, so you have to name your class accordingly. In keeping with the rest of DMP, the default class name in a file should be named ``class process_request()``. Consider the following ``index.py`` file:

.. code:: python

    from django.conf import settings
    from django.http import HttpResponse
    from django.views.generic import View
    from .. import dmp_render, dmp_render_to_string
    from datetime import datetime

    class process_request(View):
        def get(self, request):
            context = {
                'now': datetime.now().strftime(request.urlparams[0] if request.urlparams[0] else '%H:%M'),
            }
            return dmp_render(request, 'index.html', context)

    class discovery_section(View):
        def get(self, request):
            return HttpResponse('Get was called.')

        def post(self, request):
            return HttpResponse('Post was called.')

In the above ``index.py`` file, two class-based views are defined. The first is called with the url ``/homepage/index/``. The second is called with the url ``/homepage/index.discovery_section/``.

In contrast with normal function-based routing, class-based views do not require the ``@view_function`` decorator, which provides security on which functions are web-accessible. Since class-based views must extend django.views.generic.View, the security provided by the decorator is already provided. DMP assumes that **any extension of View will be accessible**.

    Python programmers usually use TitleCaseClassName (capitalized
    words) for class names. In the above classes, I'm instead using all
    lowercase (which is the style for function and variable names) so my
    URL doesn't have uppercase characters in it. If you'd rather use
    TitleCaseClassName, such as ``class DiscoverySection``, be sure your
    URL matches it, such as
    ``http://yourserver.com/homepage/index.DiscoverySection/``.

Templates Located Elsewhere
---------------------------

This impacts few users of DMP, so you may want to skip this section for now.

Suppose your templates are located in a directory outside your normal project root. For whatever reason, you don't want to put your templates in the app/templates directory.

Case 1: Templates Within Your Project Directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the templates you need to access are within your project directory, no extra setup is required. Simply reference those templates relative to the root project directory. For example, to access a template located at BASE\_DIR/homepage/mytemplates/sub1/page.html, use the following:

.. code:: python

    return dmp_render(request, '/homepage/mytemplates/sub1/page.html', context)

Note the starting slash on the path. That tells DMP to start searching at your project root.

Don't confuse the slashes in the above call with the slash used in Django's ``render`` function. When you call ``render``, the slash separates the app and filename. The above call uses ``dmp_render``, which is a different function. You should really standardize on one or the other throughout your project.

Case 2: Templates Outside Your Project Directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose your templates are located on a different disk or entirely different directory from your project. DMP allows you to add extra directories to the template search path through the ``TEMPLATES_DIRS`` setting. This setting contains a list of directories that are searched by DMP regardless of the app being referenced. To include the ``/var/templates/`` directory in the search path, set this variable as follows:

.. code:: python

    'TEMPLATES_DIRS': [
       '/var/templates/',
    ],

Suppose, after making the above change, you need to render the '/var/templates/page1.html' template:

.. code:: python

    return dmp_render(request, 'page1.html', context)

DMP will first search the current app's ``templates`` directory (i.e. the normal way), then it will search the ``TEMPLATES_DIRS`` list, which in this case contains ``/var/templates/``. Your ``page1.html`` template will be found and rendered.

Template Inheritance Across Apps
--------------------------------

You may have noticed that this tutorial has focused on a single app. Most projects consist of many apps. For example, a sales site might have an app for user management, an app for product management, and an app for the catalog and sales/shopping-cart experience. All of these apps probably want the same look and feel, and all of them likely want to extend from the **same** ``base.htm`` file.

When you run ``python3 manage.py dmp_startapp <appname>``, you get **new** ``base.htm`` and ``base_ajax.htm`` files each time. This is done to get you started on your first app. On your second, third, and subsequent apps, you probably want to delete these starter files and instead extend your templates from the ``base.htm`` and ``base_ajax.htm`` files in your first app.

In fact, in my projects, I usually create an app called ``base_app`` that contains the common ``base.htm`` html code, site-wide CSS, and site-wide Javascript. Subsequent apps simply extend from ``/base_app/templates/base.htm``. The common ``base_app`` doesn't really have end-user templates in it -- they are just supertemplates that support other, public apps.

DMP supports cross-app inheritance by including your project root (e.g. ``settings.BASE_DIR``) in the template lookup path. All you need to do is use the full path (relative to the project root) to the template in the inherits statement.

Suppose I have the following app structure:

::

    dmptest
        base_app/
            __init__.py
            media/
            scripts/
            styles/
            templates/
                site_base_ajax.htm
                site_base.htm
            views/
                __init__.py
        homepage/
            __init__.py
            media/
            scripts/
            styles/
            templates/
                index.html
            views/
                __init__.py

I want ``homepage/templates/index.html`` to extend from ``base_app/templates/site_base.htm``. The following code in ``index.html`` sets up the inheritance:

.. code:: html

            <%inherit file="/base_app/templates/site_base.htm" />

Again, the front slash in the name above tells DMP to start the lookup at the project root.

    In fact, my pages are often three inheritance levels deep:
    ``base_app/templates/site_base.htm -> homepage/templates/base.htm -> homepage/templates/index.html``
    to provide for site-wide page code, app-wide page code, and specific
    page code.

DMP Signals
-----------

DMP sends several custom signals through the Django signal dispatcher. The purpose is to allow you to hook into the router's processing. Perhaps you need to run code at various points in the process, or perhaps you need to change the request.dmp\_\* variables to modify the router processing.

Before going further with this section's examples, be sure to read the standard Django signal documentation. DMP signals are simply additional signals in the same dispatching system, so the following examples should be easy to understand once you know how Django dispatches signals.

Step 1: Enable DMP Signals
^^^^^^^^^^^^^^^^^^^^^^^^^^

Be sure your settings.py file has the following in it:

::

    'SIGNALS': True,

Step 2: Create a Signal Receiver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following creates two receivers. The first is called just before the view's process\_request function is called. The second is called just before DMP renders .html templates.

.. code:: python

    from django.dispatch import receiver
    from django_mako_plus import signals, get_template_loader

    @receiver(signals.dmp_signal_pre_process_request)
    def dmp_signal_pre_process_request(sender, **kwargs):
        request = kwargs['request']
        print('>>> process_request signal received!')

    @receiver(signals.dmp_signal_pre_render_template)
    def dmp_signal_pre_render_template(sender, **kwargs):
        request = kwargs['request']
        context = kwargs['context']            # the template variables
        template = kwargs['template']          # the Mako template object that will do the rendering
        print('>>> render_template signal received!')
        # let's return a different template to be used - DMP will use this instead of kwargs['template']
        tlookup = get_template_loader('myapp')
        template = tlookup.get_template('different.html')

The above code should be in a code file that is called during Django initialization. Good locations might be in a ``models.py`` file or your app's ``__init__.py`` file.

See the ``django_mako_plus/signals.py`` file for all the available signals you can listen for.

Translation (Internationalization)
----------------------------------

If your site needs to be translated into other languages, this section is for you. I'm sure you are aware that Django has full support for translation to other languages. If not, you should first read the standard Translation documentation at http://docs.djangoproject.com/en/dev/topics/i18n/translation/.

DMP supports Django's translation functions--with one caveat. Since Django doesn't know about Mako, it can't translate strings in your Mako files. DMP fixes this with the ``dmp_makemessages`` command. Instead of running ``python3 manage.py makemessages`` like the Django tutorial shows, run ``python3 manage.py dmp_makemessages``. Since the DMP version is an extension of the standard version, the same command line options apply to both.

    IMPORTANT: Django ignores hidden directories when creating a
    translation file. Most DMP users keep compiled templates in the
    hidden directory ``.cached_templates``. The directory is hidden on
    Unix because it starts with a period. If your cached templates are
    in hidden directories, be sure to run the command with
    ``--no-default-ignore``, which allows hidden directories to be
    searched.

    Internally, ``dmp_makemessages`` literally extends the
    ``makemessages`` class. Since Mako templates are compiled into .py
    files at runtime (which makes them discoverable by
    ``makemessages``), the DMP version of the command simply finds all
    your templates, compiles them, and calls the standard command.
    Django finds your translatable strings within the cached\_templates
    directory (which holds the compiled Mako templates).

Suppose you have a template with a header you want translated. Simply use the following in your template:

.. code:: html

    <%! from django.utils.translation import ugettext as _ %>
    <p>${ _("World History") }</p>

Run the following at the command line:

::

    python3 manage.py dmp_makemessages --no-default-ignore

Assuming you have translations set up the way Django's documentation tells you to, you'll get a new language.po file. Edit this file and add the translation. Then compile your translations:

::

    python3 manage.py compilemessages

Your translation file (language.mo) is now ready, and assuming you've set the language in your session, you'll now see the translations in your template.

    FYI, the ``dmp_makemessages`` command does everything the regular
    command does, so it will also find translatable strings in your
    regular view files as well. You don't need to run both
    ``dmp_makemessages`` and ``makemessages``

Cleaning Up
-----------

DMP caches its compiled templates in subdirectories of each app. The default locations for each app are ``app/templates/.cached_templates``, ``app/scripts/.cached_templates``, and ``app/styles/.cached_templates``, although the exact name depends on your settings.py. Normally, these cache directories are hidden and warrant your utmost apathy. However, there are times when DMP fails to update a cached template as it should. Or you might just need a pristine project without these generated files. This can be done with a Unix find command or through DMP's ``dmp_cleanup`` management command:

::

    # see what would be be done without actually deleting any cache folders
    python manage.py dmp_cleanup --trial-run

    # really delete the folders
    python manage.py dmp_cleanup

Sass also generates compiled files that you can safely remove. When you create a .scss file, Sass generates two additional files: ``.css`` and ``.css.map``. If you later remove the .scss, you leave the two generated, now orphaned, files in your ``styles`` directory. While some editors remove these files automatically, you can also remove them through DMP's ``dmp_sass_cleanup`` management command:

::

    # see what would be be done without actually deleting anything
    python manage.py dmp_sass_cleanup --trial-run

    # really delete the files
    python manage.py dmp_sass_cleanup

With both of these management commands, add ``--verbose`` to the command to include messages about skipped files, and add ``--quiet`` to silence all messages (except errors).

    You might be wondering how DMP knows whether a file is a regular
    .css or a Sass-generated one. It looks in your .css files for a line
    starting with ``/*# sourceMappingURL=yourtemplate.css.map */``. When
    it sees this marker, it decides that the file was generated by Sass
    and can be deleted if the matching .scss file doesn't exist. Any
    .css files that omit this marker are skipped.

Getting to Static Files Via Fake Templates
------------------------------------------

You might be wondering who came up with the heading of this section. Fake Templates? Let me explain. No, there is too much. Let me sum up: In rare use cases, you may want to take advantage of DMP's static files capability, even though you aren't rendering a real Mako template. For example, you might be creating HTML directly in Python but want the JS and CSS in regular .js/.jsm/.css/.cssm files.

Obviously, you should normally be using templates to generate HTML, but you might have a custom widgets that are created good old Python. If these widgets have a significant amount of JS and/or CSS, you may want to keep them in regular files instead of big ol' strings in your code.

By calling DMP's "fake template" functions, you can leverage its automatic discovery of static files, including rendering and caching of script/style template files and compilation of .scss files. DMP already knows how to cache and render, so why not let it do the work for you?

For example, suppose you are creating HTML in some code within a ``myapp`` view file. Even though you aren't using a template file, you can still include JS and CSS automatically:

.. code:: python

    from django_mako_plus import get_fake_template_css, get_fake_template_js

    def myfunction(request):
        # generate the html
        html = []
        html.append('<div>All your html content belong to us</div>')
        html.append('<div>Some more html</div>')

        # set up a context to pass into the .cssm and .jsm
        context = { 'four': 2 + 2 }

        # include/render two css files if they exist): myapp/styles/mytemplate.css and myapp/styles/mytemplate.cssm
        html.append(get_fake_template_css(request, 'myapp', 'mytemplate.fakehtml', context))

        # include/render two js files if they exist): myapp/scripts/mytemplate.js and myapp/scripts/mytemplate.jsm
        html.append(get_fake_template_js(request, 'myapp', 'mytemplate.fakehtml', context))

        # return the joined content
        return '\n'.join(html)

And no, you really didn't need the ``.fakehtml`` extension on the template name. Any extension (or no extension) will do.

Where to Now?
=============

This tutorial has been an introduction to the Django-Mako-Plus framework. The primary purpose of DMP is to combine the excellent Django system with the also excellent Mako templating system. And, as you've hopefully seen above, this framework offers many other benefits as well. It's a new way to use the Django system.

I suggest you continue with the following:

-  Go through the `Mako Templates <http://www.makotemplates.org/>`__
   documentation. It will explain all the constructs you can use in your
   html templates.
-  Read or reread the `Django
   Tutorial <http://www.djangoproject.com/>`__. Just remember as you see
   the tutorial's Django template code (usually surrounded by
   ``{{  }}``) that you'll be using Mako syntax instead (``${  }``).
-  Link to this project in your blog or online comments. I'd love to see
   the Django people come around to the idea that Python isn't evil
   inside templates. Complex Python might be evil, but Python itself is
   just a tool within templates.
