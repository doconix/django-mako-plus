.. _topics_redirecting:

Redirecting the Browser
==============================

Redirecting the browser is common in today's sites. For example, during form submissions, web applications often redirect the browser to the *same* page after a form submission (and handling with a view)--effectively switching the browser from its current POST to a regular GET. If the user hits the refresh button within his or her browser, the page simply gets refreshed without the form being submitted again. It prevents users from being confused when the browser opens a popup asking if the post data should be submitted again.

DMP provides four exceptions that redirect processing from anywhere in your codebase:

1. ``RedirectException``: Stops request processing and returns an HTTP 302 (temporary redirect) to the browser.
2. ``PermanentRedirectException``: Stops request processing and returns an HTTP 301 (permanent redirect) to the browser.
3. ``JavascriptRedirectException``: Stops request processing and returns a script-based redirect (``<script>window.location.href="...";</script>``). This is useful for times when a normal 302 doesn't work right, such as redirecting the overall browser during ajax calls.
4. ``InternalRedirectException``: Restarts the request internally with a new view function. This is the fastest way to redirect because it doesn't round trip back to the browser. In fact, the browser doesn't even know about the redirect, and the browser url does not change. The redirect happens directly within DMP's router.


Why not use Django's HttpResponseRedirect?
------------------------------------------------

Please do!  ``django.http.HttpResponseRedirect`` should be your primary method of redirection.

Then what's the point?  It's a difference in object type: Django's redirects are **HttpResponses**, while DMP's are **Exceptions**. In short, DMP's redirects are more versatile because **they can be raised anywhere in your code**. Django's redirects can only be returned from view functions.

When you raise one of the redirect exceptions, the exception bubbles up and is caught by the DMP router. DMP then converts the exception into the appropriate ``HttpResponse`` and returns to the browser.

    **Isn't this an abuse of exceptions?** In the Python world, it's common to direct program flow using exceptions: `StopIteration <https://docs.python.org/3/library/exceptions.html#StopIteration>`_ is a great example. Just be judicious and don't overuse the priviledge.



Examples
----------------------

.. code-block:: python

    from django_mako_plus import RedirectException, PermanentRedirectException, JavascriptRedirectException, InternalRedirectException

    # raise a normal redirect from anywhere in your code
    raise RedirectException('/some/new/url')

    # raise a permanent redirect from anywhere in your code
    raise PermanentRedirectException('/some/new/url')

    # raise a Javascript-based redirect from anywhere in your code
    raise JavascriptRedirectException('/some/new/url')

    # restart the routing process with a new view without returning to the browser.
    # the browser keeps the same url and doesn't know a redirect has happened.
    # the request.dmp.module and request.dmp.function variables are updated
    # to reflect the new values, but all other variables, such as request.dmp.urlparams,
    # request.GET, and request.POST remain the same as before.
    # the next line is as if the browser went to /homepage/upgrade/
    raise InternalRedirectException('homepage.views.upgrade', 'process_request')

DMP adds a custom header, ``Redirect-Exception``, to all exception-based redirects. Although you'll probably ignore this most of the time, the header allows you to further act on exception redirects in response middleware, your web server, or calling Javascript code.
