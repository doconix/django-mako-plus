#!/usr/bin/python
# -*- coding: utf-8 -*-
          
DEBUG = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


ADMINS = (
     ('Technical Wizards', 'wizards@mysite.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',   # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/tmp/calculator',                # Or path to database file if using sqlite3.
        'USER': '',                               # Not used with sqlite3.
        'PASSWORD': '',                           # Not used with sqlite3.
        'HOST': '',                               # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                               # Set to empty string for default. Not used with sqlite3.
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# where Django should find the urls.py file
ROOT_URLCONF = 'urls'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')  

# URL prefix for static files.
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    BASE_DIR,  # THIS IS A SECURITY ISSUE AND SHOULD ONLY BE DONE FOR DEVELOPMENT - DURING DEPLOYMENT, GATHER ALL YOUR STATIC FILES INTO ONE DIRECTORY OUTSIDE THE PROJECT ROOT
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
# CHANGE THIS UPON DOWNLOAD!!!
SECRET_KEY = '&kpr$d=$+(5@)mp0xn3wobq-^_zpauhstwpm@0=s4iod5d1vbw'

 
MIDDLEWARE_CLASSES = (
    # the django middleware we're using
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # our custom base_app.controller middleware
    'base_app.controller.RequestInitMiddleware',
)

    
# our django applications
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'base_app',                # the base templates/css/javascript for all other apps
    'calculator',              # the calculator app
)




###############################################################
###   Specific settings for the base_app Controller

# which of our apps will be used with the Mako engine. 
# typically this should be all of the custom apps of your project.
MAKO_ENABLED_APPS = (
    'base_app',                # the base templates/css/javascript for all other apps
    'calculator',              # the calculator app
)

# the app and project root - this code should find it automatically in most cases
import os.path
MAKO_PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

# the default app/templates/ directory is always included in the template search path
# define any additional search directories here - this allows inheritance between apps
# absolute paths are suggested
MAKO_TEMPLATES_DIRS = [ 
  os.path.join(MAKO_PROJECT_ROOT, 'base_app', 'templates'),
]

# identifies where the Mako template cache will be stored, relative to each app
MAKO_TEMPLATES_CACHE_DIR = 'cached_templates/'

# the default app and page to render in Mako when the url is too short
# the search will go as follows for the url: http://www.yourserver.com/myurl/
#  1. /myurl/index       (see the MAKO_DEFAULT_PAGE below, this tries myurl as the app with default page)
#  2. /calculator/myurl  (see the MAKO_DEFAULT_APP below, this tries the default app with myurl as the page)
#  3. If none of these are found, a 404 error is returned
MAKO_DEFAULT_APP = 'calculator'
MAKO_DEFAULT_PAGE = 'index'  

# these are included in every template by default - if you put your most-used libraries here, you won't have to import them exlicitly in templates
MAKO_DEFAULT_TEMPLATE_IMPORTS = [
  'import os, os.path, re',
]

###  End of settings for the base_app Controller
################################################################