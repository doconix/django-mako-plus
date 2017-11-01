# Django settings for Django-Mako-Plus
# this is only used during testing

import os
import shutil


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'test-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django_mako_plus',
    'tests',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django_mako_plus.RequestInitMiddleware',
]

ROOT_URLCONF = 'tests.urls'

TEMPLATES = [
    {
        'NAME': 'django_mako_plus',
        'BACKEND': 'django_mako_plus.MakoTemplates',
        'OPTIONS': {
            # functions to automatically add variables to the params/context before templates are rendered
            'CONTEXT_PROCESSORS': [
                'django.template.context_processors.static',            # adds "STATIC_URL" from settings.py
                'django.template.context_processors.debug',             # adds debug and sql_queries
                'django.template.context_processors.request',           # adds "request" object
                'django_mako_plus.context_processors.settings',         # adds "settings" dictionary
            ],

            # identifies where the Mako template cache will be stored, relative to each template directory
            'TEMPLATES_CACHE_DIR': '.cached_templates',

            # the default app and page to render in Mako when the url is too short
            'DEFAULT_PAGE': 'index',
            'DEFAULT_APP': 'tests',

            # the default encoding of template files
            'DEFAULT_TEMPLATE_ENCODING': 'utf-8',

            # these are included in every template by default - if you put your most-used libraries here, you won't have to import them exlicitly in templates
            'DEFAULT_TEMPLATE_IMPORTS': [
                'import django_mako_plus',
                'import os, os.path, re, json',
                'from django_mako_plus import django_syntax, jinja2_syntax, alternate_syntax',
            ],

            # whether to send the custom DMP signals -- set to False for a slight speed-up in router processing
            # determines whether DMP will send its custom signals during the process
            'SIGNALS': False,

            # see the DMP online tutorial for information about this setting
            # it can normally be empty
            'TEMPLATES_DIRS': [
                # '/var/somewhere/templates/',
            ],
        },
    },
    {
        'NAME': 'django',
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'NAME': 'jinja2',
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tests.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/dmp_testing_app.sqlite3',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    # SECURITY WARNING: this next line must be commented out at deployment
    BASE_DIR,
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# A logger for DMP
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG  # SECURITY WARNING: never set this True on a live site
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'dmp_simple': {
            'format': '%(levelname)s::DMP %(message)s'
        },
    },
    'handlers': {
        'dmp_console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'dmp_simple'
        },
    },
    'loggers': {
        'django_mako_plus': {
            'handlers': ['dmp_console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


