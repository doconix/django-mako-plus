#!/usr/bin/python
# -*- coding: utf-8 -*-
          
DEVELOPMENT_SERVER = True
DEBUG = DEVELOPMENT_SERVER           # This one is for Django
TEMPLATE_DEBUG = DEVELOPMENT_SERVER  # This one is for mako_controller

# The root folder of the entire site - 
import os.path
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

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

# set to your domain name - see the Django docs for how this increases security (it's ignored at when DEBUG=True above)
ALLOWED_HOSTS = [
  '.mysite.com'
]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# The default charset to encode pages as
DEFAULT_CHARSET = 'utf-8'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

# languages we support on the site
LANGUAGES = (
  ( 'en', 'English' ),
)

# the site id
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# where Django should find the urls.py file
ROOT_URLCONF = 'urls'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(SITE_ROOT, 'static_files')  

# URL prefix for static files.
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    SITE_ROOT,  # THIS IS A SECURITY ISSUE AND SHOULD ONLY BE DONE FOR DEVELOPMENT - DURING DEPLOYMENT, GATHER ALL YOUR STATIC FILES INTO ONE DIRECTORY OUTSIDE THE PROJECT ROOT
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'adsfjpqowie23424**@23420149(sdfqwes'

 
MIDDLEWARE_CLASSES = (
    # the django middleware we're using
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # our custom mako_controller middleware
    'mako_controller.RequestInitMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'extensions.authentication.ValidationCodeAccessKey',
    'extensions.authentication.SuperuserBackend',
)
    
# our django applications
IMPORTED_APPS = (
    # the django apps we're using
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
)
CUSTOM_APPS = (
    'base',                    # the base templates/css/javascript for all other apps
    'calculator',              # the calculator app
)
INSTALLED_APPS = CUSTOM_APPS + IMPORTED_APPS


# the default app/templates/ directory is always included in the template search path
# define any additional search directories here
MAKO_CONTROLLER_TEMPLATES_DIRS = [ 
  os.path.abspath(SITE_ROOT)  # allows templates to inherit from templates in other apps, such as base/templates/base.htm
]

# identifies where the Mako template cache will be stored, relative to each app
MAKO_CONTROLLER_TEMPLATES_CACHE_DIR = 'cached_templates/'

# the default page to render in Mako when no path is given
MAKO_DEFAULT_HTML_PAGE = 'index'  

# these are included in every template by default - if you put your most-used libraries here, you won't have to import them exlicitly in templates
MAKO_DEFAULT_TEMPLATE_IMPORTS = [
  'import os, os.path, re',
  'from calculator import models as cmod',
]

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
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
        'null': {
          'level': 'DEBUG',
          'class': 'django.utils.log.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': DEBUG and 'DEBUG' or 'WARNING',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['null'],  # set this to 'console' to see all the DB queries being run
            'propagate': False,
            'level':'DEBUG',
        },
    },
}
