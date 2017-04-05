T3: Pretty URL Parameters
===================================


Django is all about pretty URLs. In keeping with that philosophy, this framework has URL parameters. We've already used the first two items in the path: the first specifies the app, the second specifies the view/template. URL parameters are the third part, fourth part, and so on.

In traditional web links, you'd specify parameters using key=value pairs, as in ``/homepage/index?first=abc&second=def``. That's ugly, of course, and it's certainly not the Django way (it does still work, though).

With DMP, you have a better option. You'll specify parameters as ``/homepage/index/abc/def/``. The DMP controller makes the parameters available to your view as ``request.urlparams[0]`` and ``request.urlparams[1]``.

Suppose you have a product detail page that needs the SKU number of the product to display. A nice way to call that page might be ``/catalog/product/142233342/``. The app=catalog, view=product.py, and urlparams[0]=142233342.

These prettier links are much friendlier when users bookmark them, include them in emails, and write them down. It's all part of coding a user-friendly web site.

Note that URL parameters don't take the place of form parameters. You'll still use GET and POST parameters to submit forms. URL parameters are best used for object ids and other simple items that pages need to display.

Although this might not be the best use of urlparams, suppose we want to display our server time with user-specified format. On a different page of our site, we might present several different ``<a href>`` links to the user that contain different formats (we wouldn't expect users to come up with these urls on their own -- we'd create links for the user to click on). Change your ``index.py`` file to use a url-specified format for the date:

.. code:: python

    from django.conf import settings
    from django_mako_plus import view_function
    from .. import dmp_render, dmp_render_to_string
    from datetime import datetime

    @view_function
    def process_request(request):
        context = {
            'now': datetime.now().strftime(request.urlparams[0] if request.urlparams[0] else '%H:%M'),
        }
        return dmp_render(request, 'index.html', context)

The following links now give the time in different formats:

-  The default format: ``http://localhost:8000/homepage/index/``
-  The current hour: ``http://localhost:8000/homepage/index/%H/``
-  The month, year: ``http://localhost:8000/homepage/index/%B,%20%Y``

    If a urlparam doesn't exist, it always returns the empty string ''.
    This is slightly different than a regular Python list, which throws
    an exception when you index it beyond the length of the list. In
    DMP, request.urlparams[50] returns the empty string rather than an
    exception. The ``if`` statement in the code above can be used to
    determine if a urlparam exists or not. Another way to code a default
    value for a urlparam is
    ``request.urlparam[2] or 'some default value'``.

In some cases, you may need to use a different URL pattern than the DMP convention of ``/app/page/param1/param2/...``. DMP supports customization of the URL pattern; see `Customize the URL Pattern <#customize-the-url-pattern>`__ in the advanced topics section.

