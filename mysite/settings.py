"""
Django settings for django-mako-plus project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&kpr$d=$+(5@)mp0xn3wobq-^_zpauhstwpm@0=s4iod5d1vbw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mysite.urls'

WSGI_APPLICATION = 'mysite.wsgi.application'

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')  

MIDDLEWARE_CLASSES = (
    # put your django middleware here - I'm listing some common ones
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # our custom base_app.controller middleware (can be last in the list)
    'base_app.controller.RequestInitMiddleware',
)

# our django applications
INSTALLED_APPS = (
    # put your django apps here - I'm listing the common ones
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # then list your custom apps
    'base_app',                # the base templates/css/javascript for all other apps
    'calculator',              # the calculator app
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/db.sqlite3',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    BASE_DIR,  # THIS IS A SECURITY ISSUE AND SHOULD ONLY BE DONE FOR DEVELOPMENT - DURING DEPLOYMENT, GATHER ALL YOUR STATIC FILES INTO ONE DIRECTORY OUTSIDE THE PROJECT ROOT
)

# sample logging - the Mako controller (route_request) prints out to the log when in DEBUG mode.
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


###############################################################
###   Specific settings for the base_app Controller

# which of our apps will be used with the Mako engine. 
# typically this should be all of the custom apps of your project.
MAKO_ENABLED_APPS = (
    'base_app',                # the base templates/css/javascript for all other apps
    'calculator',              # the calculator app
)

# the default app/templates/ directory is always included in the template search path
# define any additional search directories here - this allows inheritance between apps
# absolute paths are suggested
MAKO_TEMPLATES_DIRS = [ 
  os.path.join(BASE_DIR, 'base_app', 'templates'),
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