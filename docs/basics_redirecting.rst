Redirecting the Browser
-------------------------

Redirecting the browser is common in today's sites. For example, during form submissions, web applications often redirect the browser to the *same* page after a form submission (and handling with a view)--effectively switching the browser from its current POST to a regular GET. If the user hits the refresh button within his or her browser, the page simply gets refreshed without the form being submitted again. It prevents users from being confused when the browser opens a popup asking if the post data should be submitted again.

DMP provides a Javascript-based redirect response and four exception-based redirects: The first, ``HttpResponseJavascriptRedirect``, sends a regular HTTP 200 OK response that contains Javascript to redirect the browser: ``<script>window.location.href="...";</script>``. Normally, redirecting should be done via Django's built-in ``HttpResponseRedirect`` (HTTP 302), but there are times when a normal 302 doesn't do what you need. For example, suppose you need to redirect the top-level page from an Ajax response. Ajax redirects normally only redirects the Ajax itself (not the page that initiated the call), and this default behavior is usually what is needed. However, there are instances when the entire page must be redirected, even if the call is Ajax-based. Note that this class doesn't use the tag or Refresh header method because they aren't predictable within Ajax (for example, JQuery seems to ignore them).

The four exception-based redirects allow you to raise a redirect from anywhere in your code. For example, the user might not be authenticated correctly, but the code that checks for this can't return a response object. Since these three are exceptions, they bubble all the way up the call stack to the DMP router -- where they generate a redirect to the browser.

    **Isn't using exceptions like this an abuse of exceptions?** In many languages, yes. But in the Python world, it's common to redirect program flow this way. `StopIteration <https://docs.python.org/3/library/exceptions.html#StopIteration>`_ is a great example. Just be judicious and don't overuse the priviledge.

As you might expect, ``RedirectException`` sends a normal 302 redirect and ``PermanentRedirectException`` sends a permanent 301 redirect. ``JavascriptRedirectException`` sends a redirect ``HttpResponseJavascriptRedirect`` as described above.

The fourth exception, ``InternalRedirectException``, is simpler and faster: it restarts the routing process with a different view/template within the *current* request, without changing the browser url. Internal redirect exceptions are rare and shouldn't be abused. An example might be returning an "upgrade your browser" page to a client; since the user has an old browser, a regular 302 redirect might not work the way you expect. Redirecting internally is much safer because your server stays in control the entire time.

The following code shows examples of different redirection methods:

.. code-block:: python

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
    # the request.dmp.module and request.dmp.function variables are updated
    # to reflect the new values, but all other variables, such as request.dmp.urlparams,
    # request.GET, and request.POST remain the same as before.
    # the next line is as if the browser went to /homepage/upgrade/
    raise InternalRedirectException('homepage.views.upgrade', 'process_request')

DMP adds a custom header, "Redirect-Exception", to all exception-based redirects. Although you'll probably ignore this most of the time, the header allows you to further act on exception redirects in response middleware, your web server, or calling Javascript code.
