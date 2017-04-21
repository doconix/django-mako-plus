Just Mako (Minimal DMP)
----------------------------------

Just want to render Mako templates within your existing Django project, but skip the other parts of DMP?  Want to go with standard ``urls.py`` routing?

The DMP engine can be used without any of the extras.  The following lists the minimal steps to get DMP running with an existing Django project:

**Create (or open) a standard Django project**:

::

    # install dependencies
    pip3 install django-mako-plus

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
