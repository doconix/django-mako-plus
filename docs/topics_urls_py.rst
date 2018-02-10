URL Patterns
===========================

This page describes how URL patterns are understood by DMP as well as how to modify the default pattern.

Default App and Page
---------------------------

As alluded to above, when the url doesn't contain the app and/or page, such as ``http://www.yourserver.com/``, DMP uses the default app and page specified in your  settings.py variables: ``DEFAULT_PAGE`` and ``DEFAULT_APP``.

In the following table, the default app is set to ``homepage`` and your default page is set to ``index.html``:

+----------------------------------------------------------+-------------------+------------------------+-------------------------------------------+
| URL                                                      | App               | Page                   | Notes                                     |
+----------------------------------------------------------+-------------------+------------------------+-------------------------------------------+
| ``http://www.yourserver.com/``                           | ``homepage``      | ``index.html``         |                                           |
+----------------------------------------------------------+-------------------+------------------------+-------------------------------------------+
| ``http://www.yourserver.com/account/``                   | ``account``       | ``index.html``         |                                           |
+----------------------------------------------------------+-------------------+------------------------+-------------------------------------------+
| ``http://www.yourserver.com/login/``                     | ``login``         | ``index.html``         | If ``login`` **is** one of your apps      |
+----------------------------------------------------------+-------------------+------------------------+-------------------------------------------+
| ``http://www.yourserver.com/login/``                     | ``homepage``      | ``login.html``         | If ``login`` **is not** one of your apps  |
+----------------------------------------------------------+-------------------+------------------------+-------------------------------------------+
| ``http://www.yourserver.com/account/password/``          | ``account``       | ``password.html``      |                                           |
+----------------------------------------------------------+-------------------+------------------------+-------------------------------------------+


Custom URL Patterns
--------------------------

Suppose your project requires a different URL pattern than the normal ``/app/page/param1/param2/...``. For example, you might need the user id in between the app and page: ``/app/userid/page/param1/param1...``. This is supported in two different ways.

Custom URL Patterns: Take 1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first method is done with named parameters, and it is the "normal" way to customize the url pattern. Instead of including the default\ ``django_mako_plus.urls`` module in your ``urls.py`` file, you can instead create the patterns manually. Start with the `patterns in the DMP source <http://github.com/doconix/django-mako-plus/blob/master/django_mako_plus/urls.py>`__ and modify them as needed.

The following is one of the URL patterns, modified to include the ``userid`` parameter in between the app and page:

::

    from django_mako_plus import route_request
    urlpatterns = [
        ...
        url(r'^(?P<dmp_app>[_a-zA-Z0-9\.\-]+)/(?P<userid>\d+)/(?P<dmp_page>[_a-zA-Z0-9\.\-]+)/?(?P<urlparams>.*?)/?$', route_request, name='DMP - /app/page'),
        ...
    ]

Then, in your process\_request method, be sure to include the userid parameter. This is according to the standard Django documentation with named parameters:

::

    @view_function
    def process_request(request, userid):
        ...

Be sure to use named parameters for both DMP and your custom parameters in your regular expression pattern.  Django doesn't allow both named and positional parameters in a single pattern, so we had to choose one.  Named parameters are the way to go when using DMP.

You can also "hard code" the app or page name in a given pattern. Suppose you want URLs entirely made of numbers (without any slashes) to go the user app: ``/user/views/account.py``. The pattern would hard-code the app and page as `extra options <http://docs.djangoproject.com/en/1.10/topics/http/urls/#passing-extra-options-to-view-functions>`__. In urls.py:

.. code:: python

    from django_mako_plus import route_request
    urlpatterns = [
        ...
        url(r'^(?P<user_id>\d+)$', route_request, { 'dmp_app': 'user', 'dmp_page': 'account' }, name='User Account'),
        ...
    ]

Use the following named parameters in your patterns to tell DMP which
app, page, and function to call:

-  ``(?P<dmp_app>[_a-zA-Z0-9\-]+)`` is the app name. If omitted, it is set to ``DEFAULT_APP`` in settings.
-  ``(?P<dmp_page>[_a-zA-Z0-9\-]+)`` is the view module name. If omitted, it is set to ``DEFAULT_APP`` in settings.
-  ``(?P<dmp_function>[_a-zA-Z0-9\.\-]+)`` is the function name.  If omitted, it is set to ``process_request``.
-  ``(?P<urlparams>.*)`` is the url parameters, and it should normally  span multiple slashes. The default patterns set this value to  anything after the page name. This value is split on the slash ``/``   to form the ``request.dmp.urlparams`` list. If omitted, it is set to the empty list ``[]``.

The following URL pattern can be used to embed an object ID parameter (named 'id' in this case) into DMP's conventional URL pattern (between the app name and the page name):

::

    url(r'^(?P<dmp_app>[_a-zA-Z0-9\-]+)/(?P<id>\d+)/(?P<dmp_page>[_a-zA-Z0-9\-]+)\.?(?P<dmp_function>[_a-zA-Z0-9\-]+)?/?(?P<urlparams>.*)$', route_request, name='/app/id/page(.function)(/urlparams)'),

Custom URL Patterns: Take 2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The second method is done by directly modifying the variables created in the middleware. This can be done through a custom middleware view function that runs after ``django_mako_plus.RequestInitMiddleware`` (or alternatively, you could create an extension to this class and replace the class in the ``MIDDLEWARE`` list).

Once ``RequestInitMiddleware.process_view`` creates the variables, your custom middleware can modify them in any way. As view middleware, your function will run *after* the DMP middleware by *before* routing takes place in ``route_request``.

This method of modifying the URL pattern allows total freedom since you can use python code directly. However, it would probably be done in an exceptional rather than typical case.


