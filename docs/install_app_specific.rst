Limiting DMP to Specific Apps
=======================================================

DMP normally enables itself within all "local" apps in your project.  That's the apps that are located beneath your project root.

This happens when you include DMP's URL file in your project. DMP iterates your local apps, and it adds a custom resolver for each one using ``dmp_app()``.  In turn, each resolver adds a number of patterns for its app using ``dmp_path()``.  See these `methods and _generate_patterns() in the source <http://github.com/doconix/django-mako-plus/blob/master/django_mako_plus/router/resolver.py>`_.

You can disable the automatic registration of apps with DMP by removing the ``include('', 'django_mako_plus')`` line from ``urls.py``.  Then register the specific apps you want using ``dmp_app()``.

An Example
-----------------

The following project ``urls.py`` file enables DMP-style routing on just two apps: ``polls`` and ``account``:

.. code:: python

    from django.apps import apps
    from django.conf.urls import url
    from django.contrib import admin
    from django.views.static import serve
    from django_mako_plus import dmp_app
    import os

    urlpatterns = [
        url(r'^admin/', admin.site.urls),

        # disable the normal include
        # url('', include('django_mako_plus.urls')),

        # add the DMP js file path (remove this at production)
        url(r'^django_mako_plus/(?P<path>[^/]+)', serve, { 'document_root': os.path.join(apps.get_app_config('django_mako_plus').path, 'webroot') }, name='DMP webroot (for devel)'),

        # add patterns for two apps only
        dmp_app('polls'),
        dmp_app('account'),

    ]
