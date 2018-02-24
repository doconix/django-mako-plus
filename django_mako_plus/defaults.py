# this dict of options is merged with the current project's TEMPLATES entry for DMP
DEFAULT_OPTIONS = {
    # the default app and page to render in Mako when the url is too short
    # if None (no default app), DMP will not capture short URLs
    'DEFAULT_APP': 'homepage',
    'DEFAULT_PAGE': 'index',

    # how to discover and register apps
    # 'default': register all apps that are subfolders of BASE_DIR
    # 'all': register all apps, even when pip-installed or django apps (e.g. django.contrib.admin)
    # 'none': no auto-registration; apps must be registered with `django_mako_plus.register_dmp_app()`
    'APP_DISCOVERY': 'default',

    # functions to automatically add variables to the params/context before templates are rendered
    'CONTEXT_PROCESSORS': [
        'django.template.context_processors.static',            # adds "STATIC_URL" from settings.py
        'django.template.context_processors.debug',             # adds debug and sql_queries
        'django.template.context_processors.request',           # adds "request" object
        'django.contrib.auth.context_processors.auth',          # adds "user" and "perms" objects
        'django.contrib.messages.context_processors.messages',  # adds messages from the messages framework
        'django_mako_plus.context_processors.settings',         # adds "settings" dictionary
    ],

    # identifies where the Mako template cache will be stored, relative to each template directory
    'TEMPLATES_CACHE_DIR': '__dmpcache__',

    # the default encoding of template files
    'DEFAULT_TEMPLATE_ENCODING': 'utf-8',

    # imports for every template
    'DEFAULT_TEMPLATE_IMPORTS': [
        # alternative syntax blocks within your Mako templates
        # 'from django_mako_plus import django_syntax, jinja2_syntax, alternate_syntax',

        # the next two lines are just examples of including common imports in templates
        # 'from datetime import datetime',
        # 'import os, os.path, re, json',
    ],

    # whether to send the custom DMP signals -- set to False for a slight speed-up in router processing
    # determines whether DMP will send its custom signals during the process
    'SIGNALS': False,

    # static file providers
    'CONTENT_PROVIDERS': [
        { 'provider': 'django_mako_plus.JsContextProvider' },     # adds JS context - this should normally be listed first
        { 'provider': 'django_mako_plus.CssLinkProvider' },       # generates links for app/styles/template.css
        { 'provider': 'django_mako_plus.JsLinkProvider' },        # generates links for app/scripts/template.js
        # { 'provider': 'django_mako_plus.CompileScssProvider' },   # autocompiles Scss files
        # { 'provider': 'django_mako_plus.CompileLessProvider' },   # autocompiles Less files
    ],

    # webpack providers
    'WEBPACK_PROVIDERS': [
        { 'provider': 'django_mako_plus.JsLinkProvider' },        # generates links for app/scripts/template.js
    ],

    # additional template dirs to search
    'TEMPLATES_DIRS': [
        # '/var/somewhere/templates/',
    ],
}
