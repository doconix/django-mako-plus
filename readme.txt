DESCRIPTION
===========

This project is a front controller that integrates Django with Mako templates.  Django comes with its own template system, but it's fairly weak (by design).  Mako, on the other hand, is a fantastic template system that allows full Python code within HTML pages. 

This project also includes a number of other benefits:

1. It allows calling views and html pages by convention rather than specific entries in urls.py. Any .html file on your site can be called without new entries in urls.py for every. single. new. page.

2. It introduces the idea of URL parameters (see the calculator example app in the download). 

3. It separates view functions into different files rather than all-in-one style.  This prevents huge views.py files.

4. It automatically includes CSS and JS files, and it allows Python code within these files.  These static files get connected right into the Mako template inheritance tree.

5. It uses the Mako templating engine rather than the weaker Django templating engine.  Why would I want to learn a whole new language for templating when Mako uses my favorite language: Python?

But don't worry, you'll still get all the Django goodness with ORM, views, forms, etc.



QUICK SETUP AND RUN
===================

I've distributed this as a ready-to-run Django project.  I'm hopeful that will make it easier for people to try it out.  Start by downloading the django-mako-plus .zip file from GitHub.  Unzip it to a directory on your machine.  it's a full, working project.

Then run through the following:

1. Prerequisites:
   - Install Python 3+ and ensure you can run "python" at the command prompt.
   - Run "easy_install django" or "pip install django" or otherwise install Django (https://www.djangoproject.com)
   - Run "easy_install mako" or "pip install mako" or otherwise install Mako (http://www.makotemplates.org)
   
2. Edit the settings.py file and update your settings (see the Django docs).   
   - If you just want to use sqlite3, set the NAME field to a valid filename on your system.
   - Look through the Mako settings at the end of the file (they should work as is).
   
3. Open a command prompt or terminal window and "cd" to the django-mako-plus directory.

4. Run "python manage.py syncdb" to create the database tables.
   - Say "yes" when asked to create a superuser.

5. Run "python manage.py runserver" to start the development server.

6. Take your browser to http://localhost:8000/calculator/index.html



INTEGRATING INTO AN EXISTING PROJECT
====================================

1. Copy the base_app directory into your project.  This is a standard Django application that you should install just like any other Django app.

2. Copy the Mako-specific settings at the end of the settings.py file into your project's settings.py file.  Modify them to fit your setup.



AUTHOR
======

This project is maintained by Conan C. Albrecht <ca@byu.edu>.  You can view my blog at http://warp.byu.edu/.