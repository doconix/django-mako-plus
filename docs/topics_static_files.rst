Static Files: Images and Other Media
============================================

.. contents::
    :depth: 2

Static files are files linked into your html documents like ``.css`` and ``.js`` as well as images files like ``.png`` and ``.jpg``. These are served directly by your web server (Apache, Nginx, etc.) rather than by Django because they don't require any processing. They are just copied across the Internet. Serving static files is what web servers were written for, and they are better at it than anything else.

Django-Mako-Plus works with static files the same way that traditional Django does, with one difference: the folder structure is different in DMP. The folllowing subsections describe how you should use static files with DMP.

    If you read nothing else in this tutorial, be sure to read through
    the Deployment subsection given shortly. There's a potential
    security issue with static files that you need to address before
    deploying. Specifically, you need to comment out ``BASE_DIR`` from
    the setup shown next.

Static File Setup
---------------------------

In your project's settings.py file, be sure you add the following:

.. code:: python

    STATIC_URL = '/static/'
    STATICFILES_DIRS = (
        BASE_DIR,
    )
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

Note that the last line is a serious security issue if you go to production with it (although Django disables it as long as ``DEBUG=False``). More on that later.

Development
---------------------------

During development, Django will use the ``STATICFILES_DIRS`` variable to find the files relative to your project root. You really don't need to do anything special except ensure that the ``django.contrib.staticfiles`` app is in your list of ``INSTALLED_APPS``. Django's ``staticfiles`` app is the engine that statics files during development.

Simply place media files for the homepage app in the homepage/media/ folder. This includes images, videos, PDF files, etc. -- any static files that aren't Javascript or CSS files.

Reference static files using the ``${ STATIC_URL }`` variable. For example, reference images in your html pages like this:

.. code:: html

    <img src="${ STATIC_URL }homepage/media/image.png" />

By using the ``STATIC_URL`` variable from settings in your urls rather than hard-coding the ``/static/`` directory location, you can change the url to your static files easily in the future.

Security at Deployment
---------------------------

At production/deployment, comment out ``BASE_DIR`` because it essentially makes your entire project available via your static url (a serious security concern):

.. code:: python

    STATIC_URL = '/static/'
    STATICFILES_DIRS = (
        # BASE_DIR,
    )
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

When you deploy to a web server, run ``dmp_collectstatic`` to collect your static files into a separate directory (called ``/static/`` in the settings above). You should then point your web server (Apache, Nginx, IIS, etc.) to serve this folder directly to browsers. For example, in Nginx, you'd set the following:

::

    location /static/ {
        alias /path/to/your/project/static/;
        access_log off;
        expires 30d;
    }

In Apache, you'd set the following:

Alias /static/ /path/to/your/project/static/

::

    <Directory /path/to/your/project/static/>
    Order deny,allow
    Allow from all
    </Directory>

Collecting Static Files
---------------------------

DMP comes with a management command called ``dmp_collectstatic`` that copies all your static resource files into a single subtree so you can easily place them on your web server. At development, your static files reside within the apps they support. For example, the ``homepage/media`` directory is a sibling to ``homepage/views`` and ``/homepage/templates``. This combined layout makes for nice development, but a split layout is more optimal for deployment because you have two web servers active at deployment (a traditional server like Apache doing the static files and a Python server doing the dynamic files).

A Django-Mako-Plus app has a different layout than a traditional Django app, so it comes with its own static collection command. When you are ready to publish your web site, run the following to split out the static files into a single subtree:

.. code:: python

    python3 manage.py dmp_collectstatic

This command will copy the static directories--\ ``/media/``, ``/scripts/``, and ``/styles/``--to a common subtree called ``/static/`` (or whatever ``STATIC_ROOT`` is set to in your settings). Everything in these directories is copied (except dynamic ``*.jsm/*.cssm`` files, which aren't static).

    The command copies only these three directorie out of your DMP app
    folders. Any other directories, such as ``views`` and ``templates``
    and ``mydir`` are skipped. If you need to include additional
    directories or file patterns, use the option below.

The ``dmp_collectstatic`` command has the following command-line options:

-  The commmand will refuse to overwrite an existing ``/static/``
   directory. If you already have this directory (either from an earlier
   run or for another purpose), you can 1) delete it before collecting
   static files, or 2) specify the overwrite option as follows:

::

    python3 manage.py dmp_collectstatic --overwrite

-  If you need to ignore certain directories or filenames, specify them
   with the ``--skip-dir`` and ``--skip-file`` options. These can be
   specified more than once, and it accepts Unix-style wildcards.

::

    python3 manage.py dmp_collectstatic --skip-dir=.cached_templates --skip-file=*.txt --skip-file=*.md

-  If you need to include additional directories or files, specify them
   with the ``--include`` option. This can be specified more than once,
   and it accepts Unix-style wildcards:

::

    python3 manage.py dmp_collectstatic --include-dir=global-media --include-dir=global-styles --include-file=*.png

Django Apps + DMP Apps
''''''''''''''''''''''

You might have some traditional Django apps (like the built-in ``/admin`` app) and some DMP apps (like our ``/homepage`` in this tutorial). Your Django apps need the regular ``collectstatic`` routine, and your DMP apps need the ``dmp_collectstatic`` routine.

The solution is to run both commands. Using the options of the two commands, you can either send the output from each command to *two different* static directories, or you can send them to a single directory and let the files from the second command potentially overwrite the files from the first. I suggest this second method:

::

    python3 manage.py collectstatic
    python3 manage.py dmp_collectstatic --overwrite

The above two commands will use both methods to bring files into your ``/static/`` folder. You might get some duplication of files, but the output of the commands are different enough that it should work without issues.
