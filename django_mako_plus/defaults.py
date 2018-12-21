# this dict of options is merged with the current project's TEMPLATES entry for DMP
DEFAULT_OPTIONS = {
    # the default app and page to render in Mako when the url is too short
    # if None (no default app), DMP will not capture short URLs
    'DEFAULT_APP': 'homepage',
    'DEFAULT_PAGE': 'index',

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

    # whether autoescaping of expressions is on or off
    'AUTOESCAPE': True,

    # the converter class to use for parameter conversion
    # this should be ParameterConverter or a subclass of it
    'PARAMETER_CONVERTER': 'django_mako_plus.converter.ParameterConverter',

    # whether to send the custom DMP signals -- set to False for a slight speed-up in router processing
    # determines whether DMP will send its custom signals during the process
    'SIGNALS': False,

    # static file providers
    'CONTENT_PROVIDERS': [
        {
            # adds JS context - this should normally be listed FIRST
            'provider': 'django_mako_plus.JsContextProvider',
            # 'enabled': True,
            # 'group': 'scripts',
            # 'encoder': 'django.core.serializers.json.DjangoJSONEncoder',
            # 'filepath': 'scripts/{template}.js',
            # 'skip_duplicates': False
        }, {
            # generates links for app/styles/template.css
            'provider': 'django_mako_plus.CssLinkProvider',
            # 'enabled': True,
            # 'group': 'styles',
            # 'filepath': 'styles/{template}.css',
            # 'skip_duplicates': True
        }, {
            # generates links for app/scripts/template.js
            'provider': 'django_mako_plus.JsLinkProvider',
            # 'enabled': True,
            # 'group': 'scripts',
            # 'async': False,
            # 'filepath': 'scripts/{template}.js',
            # 'skip_duplicates': False
        }, {
            # generic auto-compiler (superclass but can also be used directly)
            'provider': 'django_mako_plus.CompileProvider',
            'enabled': False,
            # 'group': 'styles',
            # 'command': ['echo', 'Subclasses should override this option'],
            # 'sourcepath': 'styles/{template}.scss',
            # 'targetpath': 'styles/{template}.css'
        }, {
            # autocompiles Scss files
            'provider': 'django_mako_plus.CompileScssProvider',
            'enabled': False,
            # 'group': 'styles',
            # 'command': [ '/usr/local/bin/sass', '--load-path=.', '{sourcepath}', '{targetpath}' ],
            # 'sourcepath': 'styles/{template}.scss',
            # 'targetpath': 'styles/{template}.css'
        }, {
            # autocompiles Less files
            'provider': 'django_mako_plus.CompileLessProvider',
            'enabled': False,
            # 'group': 'styles',
            # 'command': [ '/usr/local/bin/lessc', '--source-map', '{sourcepath}', '{targetpath}' ],
            # 'sourcepath': 'styles/{template}.less',
            # 'targetpath': 'styles/{template}.css'
        }, {
            # generic link generator (superclass but can also be used directly)
            'provider': 'django_mako_plus.LinkProvider',
            'enabled': False,
            # 'group': 'styles',
            # 'filepath': 'scripts/{template}.js',
            # 'skip_duplicates': False
        }, {
            # generates links to app/styles/__bundle__.css (see DMP docs on webpack)
            'provider': 'django_mako_plus.WebpackCssLinkProvider',
            'enabled': False,
            # 'group': 'styles',
            # 'filepath': 'styles/__bundle__.css',
            # 'skip_duplicates': True
        }, {
            # generates links to app/scripts/__bundle__.js (see DMP docs on webpack)
            'provider': 'django_mako_plus.WebpackJsLinkProvider',
            'enabled': False,
            # 'group': 'scripts',
            # 'async': False,
            # 'filepath': 'scripts/__bundle__.js',
            # 'skip_duplicates': True
        },
    ],

    # webpack file discovery (used by `manage.py dmp_webpack`)
    'WEBPACK_PROVIDERS': [
        {
            # generates links for app/styles/template.css
            'provider': 'django_mako_plus.CssLinkProvider',
            # 'enabled': True,
            # 'group': 'styles',
            # 'filepath': 'styles/{template}.css',
            # 'skip_duplicates': True
        }, {
            # generates links for app/scripts/template.js
            'provider': 'django_mako_plus.JsLinkProvider',
            # 'enabled': True,
            # 'group': 'scripts',
            # 'async': False,
            # 'filepath': 'scripts/{template}.js',
            # 'skip_duplicates': False
        },
    ],

    # additional template dirs to search
    'TEMPLATES_DIRS': [
        # '/var/somewhere/templates/',
    ],
}
