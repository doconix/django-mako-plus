.. _install_app_specific:

Limiting to Specific Apps
=======================================================

DMP normally registers patterns for all "local" apps in your project.  That's the apps that are located beneath your project root.

This happens when you include DMP's URL file in your project. DMP iterates your local apps, and it adds patterns for each using ``app_resolver()``.  See these `methods (especially _dmp_paths_for_app()) in the source <http://github.com/doconix/django-mako-plus/blob/master/django_mako_plus/router/resolver.py>`_.

You can disable the automatic registration of apps with DMP by removing the ``include('', 'django_mako_plus')`` line from ``urls.py``.  With this line removed, DMP won't inject any convention-based patterns into your project.

Now register specific apps by calling ``app_resolver()`` directly.

An Example
-----------------

The following ``urls.py`` file enables DMP-style patterns on just two apps: ``polls`` and ``account``:

.. code-block:: python

    from django.apps import apps
    from django.conf.urls import url, include
    from django.views.static import serve

    import os

    urlpatterns = [

        # dmp JS file (for DEBUG mode)
        url(
            r'^django_mako_plus/(?P<path>[^/]+)',
            serve,
            { 'document_root': os.path.join(apps.get_app_config('django_mako_plus').path, 'webroot') },
            name='DMP webroot (for devel)',
        ),

        # manually register the polls and account apps
        apps.get_app_config('django_mako_plus').register_app('polls')
        apps.get_app_config('django_mako_plus').register_app('account')

    ]
