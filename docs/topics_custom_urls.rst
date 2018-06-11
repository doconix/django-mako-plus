Custom URL Patterns
===========================

Suppose your project requires a different URL pattern than the normal ``/app/page/param1/param2/...``. For example, you might need the user id in between the app and page: ``/app/userid/page/param1/param1...``.

Overriding the Default Patterns
-----------------------------------

When you include DMP's URL file in your project, DMP adds a custom resolver for each app using ``dmp_app()``.  In turn, each resolver adds a number of patterns for its app using ``dmp_path()``.  See these `methods and _generate_patterns() in the source <http://github.com/doconix/django-mako-plus/blob/master/django_mako_plus/router/resolver.py>`_.

You can override the creation of default patterns in the call to ``dmp_app()``.  The following ``urls.py`` file adds the user id between the app and the page:

.. code:: python





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
