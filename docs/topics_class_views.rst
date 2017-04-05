Class-Based Views
=========================

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
