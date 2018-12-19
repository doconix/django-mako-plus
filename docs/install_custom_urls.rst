Custom URL Patterns
===========================

Suppose your project requires a different URL convention than the normal ``/app/page/``. For example, you might need the user id in between the app and page: e.g. ``/app/userid/page/``.


DMP's default patterns are added when you include DMP's ``urls.py`` in your project. DMP iterates your local apps, and it adds a custom resolver for each one using ``app_resolver()``.  In turn, each resolver adds a number of patterns using ``dmp_path()``.  See these `methods and _dmp_paths_for_app() in the source <http://github.com/doconix/django-mako-plus/blob/master/django_mako_plus/router/resolver.py>`_.

You can disable the automatic registration of apps with DMP by removing the ``include('', 'django_mako_plus')`` line from ``urls.py``.  With this line removed, DMP won't inject any convention-based patterns into your project.

Project Patterns
----------------------------

Per Django best practices, we'll split the patterns into a main include for the app and another file for the app. First modify your project URL file: ``mysite/urls.py``:

.. code-block:: python

    from django.apps import apps
    from django.conf.urls import url, include
    from django.views.static import serve
    import os

    urlpatterns = [

        # DMP's JS file (for DEBUG mode)
        url(
            r'^django_mako_plus/(?P<path>[^/]+)',
            serve,
            { 'document_root': os.path.join(apps.get_app_config('django_mako_plus').path, 'webroot') },
            name='DMP webroot (for devel)',
        ),

        # include the homepage app urls.py file
        url('^homepage/?', include('homepage.urls')),

    ]

Patterns for the ``homepage`` App
------------------------------------

Create an app-specific file for the homepage app: ``homepage/urls.py``.  These patterns are adapted from `DMP's default urls.py file <http://github.com/doconix/django-mako-plus/blob/master/django_mako_plus/urls.py>`_.  Each call to ``dmp_path`` includes the four routing variables in either the pattern or the kwargs.

.. code-block:: python

    from django_mako_plus import dmp_path

    urlpatterns = [
        # Because these patterns are subpatterns within the app's resolver,
        # we don't include the /app/ in the pattern -- it's already been
        # handled by the app's resolver.
        #
        # Also note how the each pattern below defines the four kwargs--
        # either as 1) a regex named group or 2) in kwargs.
        dmp_path(
            r'^(?P<userid>[0-9-]+)/(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]+)/(?P<dmp_urlparams>.+?)/?$',
            { 'dmp_app': 'homepage' },
            name='/homepage/userid/page.function/urlparams',
        ),
        dmp_path(
            r'^(?P<userid>[0-9-]+)/(?P<dmp_page>[_a-zA-Z0-9\-]+)\.(?P<dmp_function>[_a-zA-Z0-9\.\-]+)/?$',
            { 'dmp_app': 'homepage',
            'dmp_urlparams': '' },
            name='/homepage/userid/page.function',
        ),
        dmp_path(
            r'^(?P<userid>[0-9-]+)/(?P<dmp_page>[_a-zA-Z0-9\-]+)/(?P<dmp_urlparams>.+?)/?$',
            { 'dmp_app': 'homepage',
            'dmp_function': 'process_request' },
            '/homepage/userid/page/urlparams',
        ),
        dmp_path(
            r'^(?P<userid>[0-9-]+)/(?P<dmp_page>[_a-zA-Z0-9\-]+)/?$',
            { 'dmp_app': 'homepage',
                'dmp_function': 'process_request',
                'dmp_urlparams': '' },
            name='/homepage/userid/page',
        ),
        dmp_path(
            r'^(?P<userid>[0-9-]+)/?$',
            { 'dmp_app': 'homepage',
            'dmp_page': 'index',
            'dmp_function': 'process_request',
            'dmp_urlparams': '' },
            name='/homepage/userid',
        ),
    ]

The ``userid`` group in the patterns above accepts any number, plus a dash.  The dash is the DMP value for "empty".  Our pattern could actually be improved, but it'll work for this example.

View Function
---------------------

Your view function needs to change because we have an additional named group in our patternns: ``userid``.  We'll have DMP convert this parameter to an int, with a default value of 0.

.. code-block:: python

    from django.http import HttpResponse
    from django_mako_plus import view_function

    @view_function
    def process_request(request, userid:0=None):
        return HttpResponse('The userid was %s' % userid)

All view functions in the ``homepage`` need this function signature.

Test with the following urls:

* `http://localhost:8000/homepage/42/index <http://localhost:8000/homepage/-/index>`_
* `http://localhost:8000/homepage/-/index <http://localhost:8000/homepage/-/index>`_


Next Steps
----------------

We haven't added any patterns for the default app.  If ``homepage`` is our default app, we need additional patterns in the main ``urls.py`` file that don't have an app.
