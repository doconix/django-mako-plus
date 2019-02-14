import os, shutil

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

    # static file providers (see "static file" docs for full options here)
    'CONTENT_PROVIDERS': [
        # adds JS context - this should normally be listed FIRST
        { 'provider':   'django_mako_plus.JsContextProvider' },

        # Sass compiler and link generator
        # { 'provider':   'django_mako_plus.CompileScssProvider',
        #   'sourcepath': lambda p: os.path.join(p.app_config.name, 'styles', p.template_relpath + '.scss'),
        #   'targetpath': lambda p: os.path.join(p.app_config.name, 'styles', p.template_relpath + '.scss.css'),
        #   'command':    lambda p: [ shutil.which('sass'), f'--load-path="{BASE_DIR}"', p.sourcepath, p.targetpath ] },
        # { 'provider':   'django_mako_plus.CssLinkProvider',
        #   'filepath':   lambda p: os.path.join(p.app_config.name, 'styles', p.template_relpath + '.scss.css') },

        # Less compiler and link generator
        # { 'provider':   'django_mako_plus.CompileLessProvider',
        #   'sourcepath': lambda p: os.path.join(p.app_config.name, 'styles', p.template_relpath + '.less'),
        #   'targetpath': lambda p: os.path.join(p.app_config.name, 'styles', p.template_relpath + '.less.css'),
        #   'command':    lambda p: [ shutil.which('lessc'), f'--source-map', p.sourcepath, p.targetpath ] },
        # { 'provider':   'django_mako_plus.CssLinkProvider',
        #   'filepath':   lambda p: os.path.join(p.app_config.name, 'styles', p.template_relpath + '.less.css') },

        # generic compiler and link generator (see DMP docs, same options as other entries here)
        # { 'provider':   'django_mako_plus.CompileProvider' },
        # { 'provider':   'django_mako_plus.LinkProvider' },

        # link generators for regular JS and CSS: app/scripts/*.js and app/styles/*.css
        { 'provider':   'django_mako_plus.CssLinkProvider' },
        { 'provider':   'django_mako_plus.JsLinkProvider' },

        # link generators for app/scripts/__bundle__.js (webpack bundler)
        # { 'provider':   'django_mako_plus.WebpackJsLinkProvider' },
    ],

    # webpack file discovery, used by `manage.py dmp_webpack` to generate __entry__.js files
    'WEBPACK_PROVIDERS': [
        # finders for app/scripts/*.js and app/styles/*.css
        { 'provider': 'django_mako_plus.JsLinkProvider' },
        { 'provider': 'django_mako_plus.CssLinkProvider' },
    ],

    # additional template dirs to search
    'TEMPLATES_DIRS': [
        # '/var/somewhere/templates/',
    ],
}
