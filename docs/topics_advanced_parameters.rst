Parameters, Conversion, and request.urlparams
===================================================

The tutorial presented the idea of view function parameters, including automatic conversion.  This section describes the full capabilities of DMP regarding these topics.

View Function Parameters
-------------------------------------





The Lower Level: request.urlparams[ ]
-------------------------------------------

DMP's automatic typing of named parameters is based on ``request.urlparams[ ]``, a list that DMP adds to the request. This list holds all url parts *after* the /app/page/.

For example, the url ``/homepage/index/abc/def/`` has two extra parameters: ``abc`` and ``def``.  DMP makes these available as ``request.urlparams[0]`` and ``request.urlparams[1]``.

As another example, suppose you have a product detail page that needs the SKU number of the product to display. A nice way to call that page might be ``/catalog/product/142233342/``. The app=``catalog``, view=``product.py``, and urlparams[0]=``142233342``.

Note that URL parameters don't take the place of form parameters. You'll still use GET and POST parameters to submit forms. URL parameters are best used for object ids and other simple items that pages need to display, such as the product id in the previous example.

If a urlparam doesn't exist, it always returns the empty string ''. This is slightly different than a regular Python list, which throws an exception when you index it beyond the length of the list. In DMP, request.urlparams[50] returns the empty string rather than an exception. The ``if`` statement in the code above can be used to determine if a urlparam exists or not. Another way to code a default value for a urlparam is ``request.urlparam[2] or 'some default value'``.



An Example of request.urlparams
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


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

    Note that regular GET name=value pairs might be better in this specific use case.  I'm only using this example because it follows the case used throughout the tutorial.

