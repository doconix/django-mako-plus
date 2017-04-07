Customizing the URL
===========================

.. contents::
    :depth: 2

Suppose your project requires a different URL pattern than the normal ``/app/page/param1/param2/...``. For example, you might need the user id in between the app and page: ``/app/userid/page/param1/param1...``. This is supported in two different ways.

URL Patterns: Take 1
--------------------------

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

Be sure to use named parameters for both DMP and your custom parameters in your regular expression pattern.  Django doesn't allow both named and positional parameters in a single pattern.

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
--------------------------

The second method is done by directly modifying the variables created in the middleware. This can be done through a custom middleware view function that runs after ``django_mako_plus.RequestInitMiddleware`` (or alternatively, you could create an extension to this class and replace the class in the ``MIDDLEWARE`` list).

Once ``RequestInitMiddleware.process_view`` creates the variables, your custom middleware can modify them in any way. As view middleware, your function will run *after* the DMP middleware by *before* routing takes place in ``route_request``.

This method of modifying the URL pattern allows total freedom since you can use python code directly. However, it would probably be done in an exceptional rather than typical case.
