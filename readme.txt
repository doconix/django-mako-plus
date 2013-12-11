Use this if you've said: 

  "Why are Django templates weak sauce? Why not just use regular Python in templates?"
  
  "Why does Django make me list every. single. page. in urls.py?"
  
  "I'd like to include Python code in my CSS and Javascript files."
  
  "My app's views.py file is getting HUGE.  How can I split it intelligently?"
  
  

DESCRIPTION
===========

This app is a front controller that integrates Django with Mako templates.  Django comes with its own template system, but it's fairly weak (by design).  Mako, on the other hand, is a fantastic template system that allows full Python code within HTML pages. 

This app provides a number of benefits:

1. It uses the Mako templating engine rather than the weaker Django templating engine.  Why would I want to learn a whole new language for templating when Mako uses my favorite language: Python?

2. It allows calling views and html pages by convention rather than specific entries in urls.py. Any .html file on your site can be called without new entries in urls.py for every. single. new. page.  Doesn't Python favor convention over configuration?  

3. It introduces the idea of URL parameters (see the calculator example app in the download). 

4. It separates view functions into different files rather than all-in-one style.  This prevents huge views.py files.

5. It automatically includes CSS and JS files, and it allows Python code within these files.  These static files get connected right into the Mako template inheritance tree.  Yes, you can use Less or Sass, but this feature makes their use less needed.

But don't worry, you'll still get all the Django goodness with ORM, views, forms, etc.



QUICK SETUP AND RUN
===================

I've distributed this as a ready-to-run Django project.  I'm hopeful that will make it easier for people to try it out.  Start by downloading the django-mako-plus.zip file from GitHub.  Unzip it to a directory on your machine.  It's a full, working project rather than just an app.  If you just want the app rather than a full project, see the INTERGRATING... section below.  I've tested it on Python 3.3 and Django 1.6.

Then run through the following:

1. Prerequisites:
   - Install Python 3+ and ensure you can run "python" at the command prompt.
   - Run "easy_install django" or "pip install django" or otherwise install Django (https://www.djangoproject.com).  This is tested against Django 1.6.
   - Run "easy_install mako" or "pip install mako" or otherwise install Mako (http://www.makotemplates.org).  This is tested against Mako 0.9.
   
2. Edit the mysite/settings.py file and update your settings (see the Django docs).   
   - If you just want to use sqlite3, set the NAME field to a valid filename on your system.  This might be "c:\python33\db.sqlite3" on Windows or "/tmp/db.sqlite3" on Mac/*nix.
   - Look through the Mako settings at the end of the file, although they should work as is without changes.
   
3. Open a command prompt or terminal window and "cd" to the django-mako-plus directory.  This is the one that contains manage.py.

4. Run "python manage.py syncdb" to create the database tables.
   - Say "yes" when asked to create a superuser.

5. Run "python manage.py runserver" to start the development server.

6. Take your browser to http://localhost:8000/calculator/index/



QUICK SETUP FOR INTEGRATING INTO AN EXISTING PROJECT
====================================================

1. Copy the base_app directory into your project.  This is a standard Django application that you should install just like any other Django app.  The rest of the download is really just a demo, so you really only need the base_app app.

2. Copy the Mako-specific settings at the end of the settings.py file into your project's settings.py file.  Modify them to fit your setup.

3. Include the following middleware in your settings.py MIDDLEWARE_CLASSES:

    'base_app.controller.RequestInitMiddleware',

4. Include the following URLconf in your urls.py:
 
     (r'^.*$', 'base_app.controller.route_request' ),
     
   Note that this url matches *everything*, so you should place it last in urls.py.  The idea of the base_app is all requests route through the front controller base_app/controller.py -> route_request().  If you want to limit it to something like *.html, modify the URLconf above and the route_request() method accordingly.




HOW DO I CREATE NEW APPS BASED ON THIS?
=======================================

That's the exact idea!  This should be the base of other apps in your system.  Since the structure is a little different than normal Django apps, do the following to create a new app:

1. Ensure you've done the "quick setup for integrating into an existing project" above.

2. Copy (or rename) the 'calculator' directory to a new directory.  Remove or modify the calc.py, calc.html, etc. to your new needs.

3. Add your application to the settings.py INSTALLED_APPS directory.

4. Add your application to the settings.py MAKO_ENABLED_APPS directory.

You should be good to go!


AUTHOR
======

This app was developed at MyEducator.com.  It is maintained by Conan C. Albrecht <ca@byu.edu>.  You can view my blog at http://warp.byu.edu/.