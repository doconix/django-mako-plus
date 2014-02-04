# Use This If You've Said:

* Why are Django templates weak sauce? Why not just use regular Python in templates?
* Why does Django make me list every. single. page. in urls.py?
* I'd like to include Python code in my CSS and Javascript files.
* My app's views.py file is getting HUGE.  How can I split it intelligently?
  
  
# Description

This app is a front controller that integrates Django with Mako templates, among other things.  Django comes with its own template system, but it's fairly weak (by design).  Mako, on the other hand, is a fantastic template system that allows full Python code within HTML pages. 

This app provides a number of benefits:

1. It uses the Mako templating engine rather than the weaker Django templating engine.  Why would I want to learn a whole new language for templating when Mako uses my favorite language: Python?

2. It allows calling views and html pages by convention rather than specific entries in urls.py. Any .html file on your site can be called without new entries in urls.py for every. single. new. page.  Doesn't Python favor convention over configuration?  

3. It introduces the idea of URL parameters.  These allow you to embed parameters in urls, Django style (but without requiring urls.py definitions). 

4. It separates view functions into different files rather than all-in-one style.  This prevents huge views.py files.

5. It automatically includes CSS and JS files, and it allows Python code within these files.  These static files get connected right into the Mako template inheritance tree.  This is different than Less/Sass because it the variables are rendered per user (the others are typically rendered before uplaod to server).

But don't worry, you'll still get all the Django goodness with ORM, views, forms, etc.


# Installation


1. Prerequisites:
   * Install Python 3+ and ensure you can run "python" at the command prompt.
   * Run `easy_install django` or `pip install django` or otherwise install Django (https://www.djangoproject.com).  This is tested against Django 1.6.
   * Run `easy_install mako` or `pip install mako` or otherwise install Mako (http://www.makotemplates.org).  This is tested against Mako 0.9.
   
2. Install django-mako-plus with `easy_install django-mako-plus` or `pip install django-mako-plus`.
   
3. Create a normal Django project with the typical `python django-admin.py startproject <name>`.  In the tutorial below, I'll assume you called your project `test_dmp`.
  
4. In your new project directories, edit settings.py file:
   * Add `django_mako_plus.controller` to your INSTALLED_APPS:
         INSTALLED_APPS = (
             'django.contrib.admin',
             'django.contrib.auth',
             'django.contrib.contenttypes',
             'django.contrib.sessions',
             'django.contrib.messages',
             'django.contrib.staticfiles',
             'django_mako_plus.controller',
         )
   * Add `django_mako_plus.controller.router.RequestInitMiddleware` to your MIDDLEWARE CLASSES:
         MIDDLEWARE_CLASSES = (
             'django.contrib.sessions.middleware.SessionMiddleware',
             'django.middleware.common.CommonMiddleware',
             'django.middleware.csrf.CsrfViewMiddleware',
             'django.contrib.auth.middleware.AuthenticationMiddleware',
             'django.contrib.messages.middleware.MessageMiddleware',
             'django_mako_plus.controller.router.RequestInitMiddleware',
         )       
   * Add a logger to help you debug (optional but highly recommended!):
         LOGGING = {
             'version': 1,
             'disable_existing_loggers': True,
             'formatters': {
                 'simple': {
                     'format': '%(levelname)s %(message)s'
                 },
             },
             'handlers': {
                 'console':{
                     'level':'DEBUG',
                     'class':'logging.StreamHandler',
                     'formatter': 'simple'
                 },
             },
             'loggers': {
                 'django_mako_plus': {
                     'handlers': ['console'],
                     'level': DEBUG and 'DEBUG' or 'WARNING',
                     'propagate': True,
                 },
             },
         }
   * Add the Django-Mako-Plus settings:   
         ###############################################################
         ###   Specific settings for the django_mako_plus app

         # the default app/templates/ directory is always included in the template search path
         # define any additional search directories here - this allows inheritance between apps
         # absolute paths are suggested
         MAKO_TEMPLATES_DIRS = [ 
           # os.path.join(BASE_DIR, 'base_app', 'templates'),
         ]

         # identifies where the Mako template cache will be stored, relative to each app
         MAKO_TEMPLATES_CACHE_DIR = 'cached_templates/'

         # the default app and page to render in Mako when the url is too short
         # the search will go as follows for the url: http://www.yourserver.com/myurl/
         #  1. /myurl/index       (see the MAKO_DEFAULT_PAGE below, this tries myurl as the app with default page)
         #  2. /calculator/myurl  (see the MAKO_DEFAULT_APP below, this tries the default app with myurl as the page)
         #  3. If none of these are found, a 404 error is returned
         MAKO_DEFAULT_PAGE = 'index'  
         MAKO_DEFAULT_APP = 'homepage'

         # these are included in every template by default - if you put your most-used libraries here, you won't have to import them exlicitly in templates
         MAKO_DEFAULT_TEMPLATE_IMPORTS = [
           'import os, os.path, re',
         ]

         ###  End of settings for the base_app Controller
         ################################################################
5. Change to your project directory, then create a new Django-Mako-Plus app with `python manage.py dmp_startapp <app name>`.  In the tutorial below, I'll assume you called your app `calculator`.
6. Follow the tutorial below to see the power of Django-Mako-Plus.

# Tutorial

I assume you've just installed Django-Mako-Plus according to the instructions above.  You should have a `dmp_test` project directory that contains a `calculator` app.  Let's explore the directory structure of your new app:

        

## 

1. Create your project the regular Django way: django-admin.py startproject mysite

2. In addition to the normal settings.py changes the tutorial does (such as your database settings), add the following to the bottom of your settings.py file:

3. Create a new app using the django-mako-plus format rather than the standard Django format:

  python manage.py startdmpapp
  
extending across apps
static location
logging
settings middleware
settings apps
urls.py





# AUTHOR

This app was developed at MyEducator.com.  It is maintained by Conan C. Albrecht <ca@byu.edu>.  You can view my blog at http://warp.byu.edu/.