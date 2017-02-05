
# Use This If You've Said...

* Is there an alternative to the Django templating language?
* Why are Django templates weak sauce? Why not just use regular Python in templates?
* Why does Django make me list every. single. page. in urls.py?
* I'd like to include Python code in my CSS and Javascript files.


# Quick Start


```bash
# install django, mako, and DMP
pip3 install django mako django-mako-plus

# create a new project with a 'homepage' app
python3 -m django startproject --template=http://cdn.rawgit.com/doconix/django-mako-plus/master/project_template.zip mysite
cd mysite
python3 manage.py startapp --template=http://cdn.rawgit.com/doconix/django-mako-plus/master/app_template.zip --extension=py,htm,html homepage

# open mysite/settings.py and append 'homepage' to the INSTALLED_APPS list
INSTALLED_APPS = [
    ...
    'homepage',
]

# run initial migrations and run the server
python3 manage.py migrate
python3 manage.py runserver

# Open a browser to http://localhost/

```

> Note that on some machines, `pip3` is `pip` and `python3` is `python`.  Python 3+ is required.

# Compatability

DMP works with Python 3+ and Django 1.8+.

DMP can be used alongside regular Django templates, Jinja2 templates, and other third-party apps (including embedding these other tags within DMP templates when needed).  It plugs in via the regular `urls.py` mechanism, just like any other view.  Be assured that it plays nicely with the other children.


# Table of Contents
<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Use This If You've Said...](#use-this-if-youve-said)
- [Quick Start](#quick-start)
- [Open a browser to http://localhost/](#open-a-browser-to-httplocalhost)
- [Compatability](#compatability)
- [Table of Contents](#table-of-contents)
- [Description](#description)
	- [Where Is DMP Used?](#where-is-dmp-used)
	- [Why Mako instead of Jinja2, Cheetah, or <insert template language here>?](#why-mako-instead-of-jinja2-cheetah-or-insert-template-language-here)
	- [Can I use DMP with other Django apps?](#can-i-use-dmp-with-other-django-apps)
	- [Comparison with Django Syntax](#comparison-with-django-syntax)
- [Installation](#installation)
	- [Upgrade Notes for DMP 3.8](#upgrade-notes-for-dmp-38)
	- [Python 3+](#python-3)
	- [Install Django, Mako, and DMP](#install-django-mako-and-dmp)
	- [Create a Django project](#create-a-django-project)
	- [Modify an existing Django project](#modify-an-existing-django-project)
		- [Edit Your `settings.py` File:](#edit-your-settingspy-file)
		- [Enable the Django-Mako-Plus Router](#enable-the-django-mako-plus-router)
	- [Create a DMP-Style App](#create-a-dmp-style-app)
	- [Load it Up!](#load-it-up)
	- [Huh? "app homepage is not a designated DMP app"?](#huh-app-homepage-is-not-a-designated-dmp-app)
	- [Convert Existing Apps to DMP](#convert-existing-apps-to-dmp)
	- [Installing Django in a Subdirectory](#installing-django-in-a-subdirectory)
- [Tutorial](#tutorial)
	- [The DMP Structure](#the-dmp-structure)
	- [Routing Without urls.py](#routing-without-urlspy)
	- [Adding a View Function](#adding-a-view-function)
		- [The Render Functions](#the-render-functions)
		- [Convenience Functions](#convenience-functions)
		- [Can't I Use the Django API?](#cant-i-use-the-django-api)
	- [URL Parameters](#url-parameters)
	- [A Bit of Style](#a-bit-of-style)
	- [A Bit of Style, Reloaded](#a-bit-of-style-reloaded)
	- [Static and Dynamic Javascript](#static-and-dynamic-javascript)
	- [Minification of JS and CSS](#minification-of-js-and-css)
	- [Ajax Calls](#ajax-calls)
	- [Really, a Whole New File for Ajax?](#really-a-whole-new-file-for-ajax)
	- [Importing Python Modules into Templates](#importing-python-modules-into-templates)
	- [Mime Types and Status Codes](#mime-types-and-status-codes)
	- [Static Files, Your Web Server, and DMP](#static-files-your-web-server-and-dmp)
		- [Static File Setup](#static-file-setup)
		- [Development](#development)
		- [Security at Deployment (VERY Important)](#security-at-deployment-very-important)
		- [Collecting Static Files](#collecting-static-files)
			- [Django Apps + DMP Apps](#django-apps-dmp-apps)
	- [Redirecting](#redirecting)
- [Deployment Recommendations](#deployment-recommendations)
	- [Deployment Tutorials](#deployment-tutorials)
- [Advanced Topics](#advanced-topics)
	- [Useful Variables](#useful-variables)
	- [Customize the URL Pattern](#customize-the-url-pattern)
		- [URL Patterns: Take 1](#url-patterns-take-1)
		- [URL Patterns: Take 2](#url-patterns-take-2)
	- [CSRF Tokens](#csrf-tokens)
	- [Behind the CSS and JS Curtain](#behind-the-css-and-js-curtain)
	- [Using Django and Jinja2 Tags and Syntax](#using-django-and-jinja2-tags-and-syntax)
	- [Expression containing Django template syntax (assuming name was created in the view.py)](#expression-containing-django-template-syntax-assuming-name-was-created-in-the-viewpy)
	- [Full Django code block, with Mako creating the variable first](#full-django-code-block-with-mako-creating-the-variable-first)
	- [Third-party, crispy form tags (assume my_formset was created in the view.py)](#third-party-crispy-form-tags-assume-myformset-was-created-in-the-viewpy)
		- [Jinja2, Mustache, Cheetah, and <insert template engine>.](#jinja2-mustache-cheetah-and-insert-template-engine)
		- [Local Variables](#local-variables)
	- [Rending Templates the Standard Way: `render()`](#rending-templates-the-standard-way-render)
	- [Rendering Partial Templates (Ajax!)](#rendering-partial-templates-ajax)
	- [Sass Integration](#sass-integration)
	- [Class-Based Views](#class-based-views)
	- [Templates Located Elsewhere](#templates-located-elsewhere)
		- [Case 1: Templates Within Your Project Directory](#case-1-templates-within-your-project-directory)
		- [Case 2: Templates Outside Your Project Directory](#case-2-templates-outside-your-project-directory)
	- [Template Inheritance Across Apps](#template-inheritance-across-apps)
	- [DMP Signals](#dmp-signals)
		- [Step 1: Enable DMP Signals](#step-1-enable-dmp-signals)
		- [Step 2: Create a Signal Receiver](#step-2-create-a-signal-receiver)
	- [Translation (Internationalization)](#translation-internationalization)
	- [Cleaning Up](#cleaning-up)
	- [Getting to Static Files Via Fake Templates](#getting-to-static-files-via-fake-templates)
- [Where to Now?](#where-to-now)

<!-- /TOC -->

# Description

This app is a template engine that integrates the excellent Django framework with the also excellent Mako templating syntax.  It conforms to the Django API and plugs in as a standard engine.

1. DMP uses the **Mako templating engine** rather than the weaker Django templating engine.  Why would I want to learn a whole new language for templating when Mako uses my favorite language: Python?

2. DMP allows **calling views and html pages by convention** rather than specific entries in urls.py. Any .html file on your site can be called without new entries in urls.py for every. single. new. page.  Doesn't Python favor convention over configuration?

3. DMP introduces the idea of URL parameters.  These allow you to embed parameters in urls, Django style--meaning you can use pretty URLs like http://myserver.com/abc/def/123/ **without explicit entries in urls.py** and without the need for traditional (i.e. ulgy) ?first=abc&second=def&third=123 syntax.

4. DMP separates view functions into different files rather than all-in-one style.  Anyone who has programmed Django long knows that the single views.py file in each app often gets looooonnng.  Splitting logic into separate files keeps things more orderly.

5. Optionally, DMP automatically includes CSS and JS files, and it allows Python code within these files.  These static files get included in your web pages without any explicit declaration of `<link>` or `<script>` elements.  This means that `mypage.css` and `mypage.js` get linked in `mypage.html` automatically.  Python code within these support files means your CSS can change based on user or database entries.

6. Optionally, DMP integrates with Sass by automatically running `scss` on updated .scss files.

> Author's Note: Django comes with its own template system, but it's fairly weak (by design).  Mako, on the other hand, is a fantastic template system that allows full Python code within HTML pages.  The primary reason Django doesn't allow full Python in its templates is the designers want to encourage you and I to keep template logic simple.  I fully agree with this philosophy.  I just don't agree with the "forced" part of this philosophy.  The Python way is rather to give freedom to the developer but train in the correct way of doing things.  Even though I fully like Python in my templates, I still keep them fairly simple.  Views are where your logic goes.

## Where Is DMP Used?

This app was developed at MyEducator.com, primarily by Dr. Conan C. Albrecht <doconix@gmail.com>.  Please email me if you find errors with this tutorial or have suggestions/fixes.  In addition to several production web sites, I use the framework in my Django classes at BYU.  120+ students use the framework each year, and many have taken it to their companies upon graduation.  At this point, the framework is quite mature and robust.  It is fast and stable.

I've been told by some that DMP has a lot in common with Rails.  When I developed DMP, I had never used RoR, but good ideas are good ideas wherever they are found, right? :)


## Why Mako instead of Jinja2, Cheetah, or <insert template language here>?

Python has several mature, excellent templating languages.  Both Mako and Jinja2 are fairly recent yet mature systems.  Both are screaming fast.  Cheetah is an older system but has quite a bit of traction.  It wasn't a clear choice of one over the rest.

Mako itself is very stable, both in terms of "lack of bugs" and in "completed feature set".  Today, the Mako API almost never changes because it does exactly what it needs to do and does it well.  This make it an excellent candidate for server use.

The short answer is I liked Mako's approach the best.  It felt the most Pythonic to me.  Jinja2 may feel more like Django's built-in template system, but Mako won out because it looked more like Python--and the point of DMP is to include Python in templates.


## Can I use DMP with other Django apps?

Yes. DMP plugs in as a regular templating engine per the standard Django API.

The hook for most apps is the `urls.py` file.  Just be sure that DMP's line in this file comes *last*.  DMP's line is a wildcard, so it matches most urls.  As long as the other app urls are listed first, Django will give them preference.

Note also that other apps likely use Django's built-in templating system rather than DMP's Mako templating system.  The two templating systems work fine side by side, so other apps should render fine the normal Django way and your custom apps will render fine with Mako.

Further, if you temporarily need to switch to Django templating syntax, [you can do that with ease](#using-django-and-jinja2-tags-and-syntax).  This allows the use of Django-style tags and syntax right within your Mako code.  No new files needed.


## Comparison with Django Syntax

If you have read through the Django Tutorial, you've seen examples for templating in Django.  While the rest of Django, such as models, settings, migrations, etc., is the same (with or without DMP), the way you do templates will obviously change with DMP.  The following examples should help you understand the different between two template systems.

Note in the examples how the DMP column normally uses standard Python syntax, with no extra language to learn:


<table>
  <tr>
      <td colspan="2"></td>
  </tr><tr>
    <th>Django</th>
    <th>DMP (Mako)</th>
  </tr><tr>
    <td colspan="2"><b>Output the value of the question variable:</b></td>
  </tr><tr>
    <td><pre><code>{{ question }}</code></pre></td>
    <td><pre><code>${ question }</code></pre></td>
  </tr><tr>
    <td colspan="2">Call a method on the User object (DMP version is a normal method call, with parameters if needed):</td>
  </tr><tr>
    <td><pre><code>{{ user.get_full_name }}</code></pre></td>
    <td><pre><code>${ user.get_full_name() }</code></pre></td>
  </tr><tr>
    <td colspan="2">Iterate through a relationship:</td>
  </tr><tr>
    <td><pre><code>&lt;ul&gt;
&nbsp;&nbsp;{% for choice in question.choice_set.all %}
&nbsp;&nbsp;&nbsp;&nbsp;&lt;li&gt;{{ choice.choice_text }}&lt;/li&gt;
&nbsp;&nbsp;{% endfor %}
&lt;/ul&gt;</code></pre></td>
    <td><pre><code>&lt;ul&gt;
&nbsp;&nbsp;%for choice in question.choice_set.all():
&nbsp;&nbsp;&nbsp;&nbsp;&lt;li&gt;${ choice.choice_text }&lt;/li&gt;
&nbsp;&nbsp;%endfor
&lt;/ul&gt;</code></pre></td>
  </tr><tr>
    <td colspan="2">Set a variable:</td>
  </tr><tr>
    <td><pre><code>{% with name="Sam" %}</code></pre></td>
    <td><pre><code>&lt;% name = &quot;Sam&quot; %&gt;</code></pre></td>
  </tr><tr>
    <td colspan="2">Format a date:</td>
  </tr><tr>
    <td><pre><code>{{ value|date:"D d M Y" }}</code></pre></td>
    <td><pre><code>${ value.strftime('%D %d %M %Y') }</code></pre></td>
  </tr><tr>
    <td colspan="2">Join a list:</td>
  </tr><tr>
    <td><pre><code>{{ mylist | join:', ' }}</code></pre></td>
    <td><pre><code>${ ', '.join(mylist) }</code></pre></td>
  </tr><tr>
    <td colspan="2">Use the /static prefix:</td>
  </tr><tr>
    <td><pre><code>{% load static %}
&lt;img src=&quot;{% get_static_prefix %}images/hi.jpg&quot;/&gt;</code></pre></td>
    <td><pre><code>&lt;img src=&quot;${ STATIC_ROOT }images/hi.jpg&quot;/&gt;</code></pre></td>
  </tr><tr>
    <td colspan="2">Call a Python method:</td>
  </tr><tr>
    <td>Requires a custom tag, unless a built-in tag provides the behavior.</td>
    <td>Any Python method can be called:
<pre><code>&nbsp;&nbsp;&lt;%! import random %&gt;
&nbsp;&nbsp;${ random.randint(1, 10) }</code></pre></td>
  </tr><tr>
    <td colspan="2">Output a default if empty:</td>
  </tr><tr>
    <td><pre><code>{{ value | default:"nothing" }}</code></pre></td>
    <td>Use a boolean:
<pre><code>&nbsp;&nbsp;${ value or "nothing" }</code></pre>

or use a Python if statement:
<pre><code>&nbsp;&nbsp;${ value if value != None else "nothing" }</code></pre>
    </td>
  </tr><tr>
    <td colspan="2">Run arbitrary Python (keep it simple, Tex!):</td>
  </tr><tr>
    <td>Requires a custom tag</td>
    <td><pre><code>&lt;%
&nbsp;&nbsp;i = 1
&nbsp;&nbsp;while i &lt; 10:
&nbsp;&nbsp;&nbsp;&nbsp;context.write(&#x27;&lt;p&gt;Testing {0}&lt;/p&gt;&#x27;.format(i))
&nbsp;&nbsp;&nbsp;&nbsp;i += 1
%&gt;</code></pre></td>
  </tr><tr>
    <td colspan="2">Inherit another template:</td>
  </tr><tr>
    <td><pre><code>{% extends "base.html" %}</code></pre></td>
    <td><pre><code>&lt;%inherit file=&quot;base.htm&quot; /&gt;</code></pre></td>
  </tr><tr>
    <td colspan="2">Override a block:</td>
  </tr><tr>
    <td><pre><code>{% block title %}My amazing blog{% endblock %}</code></pre></td>
    <td><pre><code>&lt;%block name="title"&gt;My amazing blog&lt;/%block&gt;</code></pre></td>
  </tr><tr>
    <td colspan="2">Link to a CSS file:</td>
  </tr><tr>
    <td>Place in each template:
<pre><code>&nbsp;&nbsp;&lt;link rel=&quot;stylesheet&quot; type=&quot;text/css&quot; href=&quot;...&quot;&gt;</code></pre></td>
    <td>Simply name the .css/.js file the same name as your .html template.  DMP will include the link automatically.</td>
  </tr><tr>
    <td colspan="2">Perform per-request logic in CSS or JS files:</td>
  </tr><tr>
    <td>Create an entry in urls.py, create a view, and render a template for the CSS or JS.</td>
    <td>Simply name the .css file as name.cssm for each name.html template.  DMP will render the template and include it automatically.</td>
  </tr>
</table>


# Installation

Note: If you need to use DMP 2.7, follow the [old installation instructions](http://github.com/doconix/django-mako-plus/blob/8fb0ccf942546b7ff241fd877315a18764f2dd3f/readme.md).  Be sure to use `pip3 install django-mako-plus==2.7.1` to get the old DMP codebase.  As of DMP 3.0, Python 2 is no longer supported.



## Upgrade Notes for DMP 3.8

In **January, 2017**, Django-Mako-Plus 3.8 was released.  It requires a few changes to projects created with previous versions.  Please adjust the following in your project:

* Do a sitewide search for `get_template_css` and `get_template_js`.  These will normally be found in `base.htm` and `base-ajax.htm`.
Remove the `import` line for these two commands.  The import is no longer necessary.  Replace them with the new versions of the following functions (note that the function signature have changed):

```
${ django_mako_plus.link_css(self) }

...

${ django_mako_plus.link_js(self) }
```

* In your `urls.py` file, change the DMP line to `include` the DMP urls.  A bare bones `urls.py` file would look like the following:

```python
from django.conf.urls import include, url

urlpatterns = [
    url('', include('django_mako_plus.urls')),
]
```

* In your `settings.py` file, ensure that DMP is imported in the `DEFAULT_TEMPLATE_IMPORTS` list:

```python
'DEFAULT_TEMPLATE_IMPORTS': [
    'import django_mako_plus',
]
```


* Clean out all the cached template files.  This can be done with the command:

```
python manage.py dmp_cleanup
```

* DMP no longer uses `URL_START_INDEX`.  If you set this to something other than `0`, see [Installing Django in a Subdirectory](#installing-django-in-a-subdirectory) to modify your `urls.py` for your prefix.

* This version of DMP no longer uses `request.dmp_router_page_full`.  If your code happens to use this variable, post a question to the project GitHub page or email me (Conan). I don't think anyone is using this variable outside of the DMP source code.

* The funtion signatures in the `static_files` module have changed.  If you use any of these directly, please make the appropriate modifications.  I don't think anyone is using these outside of the DMP source code.

## Python 3+

Install Python and ensure you can run `python3` (or `python`) at the command prompt.  The framework requires Python 3.x.



## Install Django, Mako, and DMP

DMP 3 works with Django 1.8+ and Mako 1.0+.  We will support Django 2.0 when it is released.

Install with the python installer:

```
pip3 install django
pip3 install mako
pip3 install django-mako-plus
```

Note that on Windows, it might be called simply `pip`:

```
pip install django
pip install mako
pip install django-mako-plus
```


## Create a Django project

Create a Django project, but specify that you want a DMP-style project layout:

```
python3 -m django startproject --template=http://cdn.rawgit.com/doconix/django-mako-plus/master/project_template.zip mysite
```

In addition to giving you the DMP project directories, this command automatically adds the required pieces to your `settings.py` and `urls.py` files.

You can, of course, name your project anything you want, but in the sections below, I'll assume you called your project `mysite`.

Don't forget to migrate to synchronize your database.  The apps in a standard Django project (such as the session app) need a few tables created for you to run the project.

```
python3 manage.py migrate
```

That's it!  Skip the next section and go to [Create a DMP-Style App](#create-a-dmp-style-app).



## Modify an existing Django project

If you need to add DMP to an existing Django project, follow the steps in this section.

If you instead created a project per the previous section, these steps have been done for you.  Stand up, clap your hands together, and skip ahead to [Create a DMP-Style App](#create-a-dmp-style-app).


#### Edit Your `settings.py` File:

Add `django_mako_plus` to the end of your `INSTALLED_APPS` list:

```python
INSTALLED_APPS = [
    ...
    'django_mako_plus',
]
```

Add `django_mako_plus.RequestInitMiddleware` to your `MIDDLEWARE` list:

```python
MIDDLEWARE = [
    ...
    'django_mako_plus.RequestInitMiddleware',
    ...
```

Add a logger to help you debug (optional but highly recommended!):

```python
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG  # never set this True on a live site
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
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

Add the Django-Mako-Plus engine to the `TEMPLATES` list.   Note that a standard Django project already has the `TEMPLATES = ` line.

```python
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
                'django.contrib.auth.context_processors.auth',          # adds "user" and "perms" objects
                'django.contrib.messages.context_processors.messages',  # adds messages from the messages framework
                'django_mako_plus.context_processors.settings',         # adds "settings" dictionary
            ],

            # identifies where the Mako template cache will be stored, relative to each template directory
            'TEMPLATES_CACHE_DIR': '.cached_templates',

            # the default app and page to render in Mako when the url is too short
            'DEFAULT_PAGE': 'index',
            'DEFAULT_APP': 'homepage',

            # the default encoding of template files
            'DEFAULT_TEMPLATE_ENCODING': 'utf-8',

            # imports for every template
            'DEFAULT_TEMPLATE_IMPORTS': [
                # import DMP (required)
                'import django_mako_plus',

                # uncomment this next line to enable alternative syntax blocks within your Mako templates
                # 'from django_mako_plus import django_syntax, jinja2_syntax, alternate_syntax

                # the next two lines are just examples of including common imports in templates
                # 'from datetime import datetime',
                # 'import os, os.path, re, json',
            ],

            # whether to send the custom DMP signals -- set to False for a slight speed-up in router processing
            # determines whether DMP will send its custom signals during the process
            'SIGNALS': False,

            # whether to minify using rjsmin, rcssmin during 1) collection of static files, and 2) on the fly as .jsm and .cssm files are rendered
            # rjsmin and rcssmin are fast enough that doing it on the fly can be done without slowing requests down
            'MINIFY_JS_CSS': True,

            # the name of the SASS binary to run if a .scss file is newer than the resulting .css file
            # happens when the corresponding template.html is accessed the first time after server startup
            # if DEBUG=False, this only happens once per file after server startup, not for every request
            # specify the binary in a list below -- even if just one item (see subprocess.Popen)

            # Python 3.3+:
            #'SCSS_BINARY': [ shutil.which('scss'), '--unix-newlines' ],

            # Python 3.0 to 3.2:
            #'SCSS_BINARY': [ '/path/to/scss', '--unix-newlines' ],

            # Disabled (no sass integration)
            'SCSS_BINARY': None,

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
]
```

Add the following to serve your static files.  Note that a standard Django project already has the first `STATIC_URL = ` line.

```python
STATIC_URL = '/static/'   # you probably already have this
STATICFILES_DIRS = (
    # SECURITY WARNING: this next line must be commented out at deployment
    BASE_DIR,
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```


#### Enable the Django-Mako-Plus Router

Add the Django-Mako-Plus router **as the last pattern** in your `urls.py` file (the default admin is also included here for completeness):

```python
from django.conf.urls import url, include

urlpatterns = [
    # urls for any third-party apps go here

    # the DMP router - this should be the last line in the list
    url('', include('django_mako_plus.urls')),
]
```

## Create a DMP-Style App

Change to your project directory in the terminal/console, then create a new Django-Mako-Plus app with the following:

```python
python3 manage.py startapp --template=http://cdn.rawgit.com/doconix/django-mako-plus/master/app_template.zip --extension=py,htm,html homepage
```

**After** the new `homepage` app is created, add your new app to the `INSTALLED_APPS` list in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'homepage',
]
```

Congratulations.  You're ready to go!


## Load it Up!

Start your web server with the following:

```python
python3 manage.py runserver
```

If you get a message about unapplied migrations, ignore it for now and continue.

Open your web browser to [http://localhost:8000/](http://localhost:8000/).  You should see a message welcoming you to the homepage app.

If everything is working, skip ahead to the tutorial.


## Huh? "app homepage is not a designated DMP app"?

If DMP tells you that an app you're trying to access "is not a designated DMP app", you missed something above.  Rather than go above and trying again, go on to the next section on converting existing apps for a summary of everything needed to make a valid DMP app.  You're likely missing something in this list, and by going through this next section, you'll ensure all the needed pieces are in place.  I'll bet you didn't set the `DJANGO_MAKO_PLUS = True` part in your app's init file.  Another possible reason is you didn't list `homepage` as one of your `INSTALLED_APPS` as described above.


## Convert Existing Apps to DMP

Already have an app that you'd like to switch over?  Just do the following:

* Ensure your app is listed in your `settings.py` file's `INSTALLED_APPS` list.

* Create folders within your app so you match the following structure:

```
your-app/
    __init__.py
    media/
    scripts/
    styles/
    templates/
    views/
        __init__.py
```

* Add the following to `your-app/__init__.py`.  This signals that your app is meant to be used with DMP.  If you don't have this variable, DMP will complain that your app isn't a 'DMP app'.

```python
DJANGO_MAKO_PLUS = True
```

* Go through your existing `your-app/views.py` file and move the functions to new files in the `your-app/views/` folder.  You need a .py file for *each* web-accessible function in your existing views.py file.  For example, if you have an existing views.py function called `do_something` that you want accessible via the url `/your-app/do_something/`, create a new file `your-app/views/do_something.py`.  Inside this new file, create the function `def process_request(request):`, and copy the contents of the existing function within this function.  Decorate each process_request with the `@view_function` decorator.

* Clean up: once your functions are in new files, you can remove the `your-app/views.py` file.  You can also remove all the entries for your app in `urls.py`.


## Installing Django in a Subdirectory

This section is for those that need Django is a subdirectory, such as `/mysite`.  If your Django installation is at the root of your domain, skip this section.

In other words, suppose your Django site isn't the only thing on your server.  Instead of the normal url pattern, `http://www.yourdomain.com/`, your Django installation is at `http://www.yourdomain.com/mysite/`.  All apps are contained within this `mysite/` directory.

This is accomplished in the normal Django way.  Adjust your `urls.py` file to include the prefix:

```
url('^mysite/', include('django_mako_plus.urls')),
```

# Tutorial


I'll assume you've just installed Django-Mako-Plus according to the instructions above.  You should have a `dmp_test` project directory that contains a `homepage` app.  I'll further assume you know how to open a terminal/console and `cd` to the `dmp_test` directory.  Most of the commands below are typed into the terminal in this directory.

**Quick Start:** You already have a default page in the new app, so fire up your server with `python3 manage.py runserver` and go to [http://localhost:8000/homepage/index/](http://localhost:8000/homepage/index/).

You should see a congratulations page.  If you don't, go back to the installation section and walk through the steps again.  Your console might have valuable error messages to help troubleshoot things.

## The DMP Structure

Let's explore the directory structure of your new app:

```
homepage/
    __init__.py
    media/
    scripts/
    styles/
    templates/
        base_ajax.htm
        base.htm
        index.html
    views/
        __init__.py
```

The directories should be fairly self-explanatory. Note they are **different** than a traditional Django app structure.  Put images and other support files in media/, Javascript in scripts/, CSS in styles/, html files in templates/, and Django views in views/.

The following setting is automatically done when you run `dmp_startapp`, but if you created your app structure manually, DMP-enabled apps must have the following in the `appname/__init__.py` file:

```python
DJANGO_MAKO_PLUS = True
```

Let's start with the two primary html template files: `base.htm` and `index.html`.

`index.html` is pretty simple:

```html
<%inherit file="base.htm" />

<%block name="content">
    <div class="content">
      <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
      <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
    </div>
</%block>
```

If you are familiar with Django templates, you'll recognize the template inheritance in the `<%inherit/>` tag.  However, this is Mako code, not Django code, so the syntax is a little different.  The file defines a single block, called `content`, that is plugged into the block by the same name in the code below.

The real HTML is kept in the `base.htm` file.  It looks like this:

```html
## this is the skeleton of all pages on in this app - it defines the basic html tags

<!DOCTYPE html>
<html>
  <meta charset="UTF-8">
  <head>

    <title>homepage</title>

    ## add any site-wide scripts or CSS here; for example, jquery:
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>

    ## render the styles with the same name as this template and its supertemplates
    ${ django_mako_plus.link_css(self) }

  </head>
  <body>

    <header>
        Welcome to the homepage app!
    </header>

    <%block name="content">
        Site content goes here in sub-templates.
    </%block>

    ## render the scripts with the same name as this template and its supertemplates
    ${ django_mako_plus.link_js(self) }

  </body>
</html>
```

Pay special attention to the `<%block name="content">` section, which is overridden in `index.html`.  The page given to the browser will look exactly like `base.htm`, but the `content` block will come from `index.html` rather than the one defined in the supertemplate.

The purpose of the inheritance from `base.htm` is to get a consistent look, menu, etc. across all pages of your site.  When you create additional pages, simply override the `content` block, similar to the way `index.html` does it.

> Don't erase anything in the base.htm file.  In particular, link_css, and link_js are important parts of DMP.  As much as you probably want to clean up the mess, try your best to leave them alone.  These are not the code lines you are looking for.  Move along.

**AttributeError: 'Undefined' object has no attribute 'link_css' / 'link_js'???**

If you get this error, you might need to update a setting in `settings.py`.  Ensure that DMP is imported in the `DEFAULT_TEMPLATE_IMPORTS` list:

```python
'DEFAULT_TEMPLATE_IMPORTS': [
    'import django_mako_plus',
]
```

Then clear out the compiled templates caches:

```
python manage.py dmp_cleanup
```


## Routing Without urls.py

In the installation procedures above, you set your urls.py file to look something like the following:

```python
from django_mako_plus import route_request

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^.*$', route_request),
]
```

The regular expression in the last line, `^.*$`, is a wildcard that matches everything.  It tells every url to go to the Django-Mako-Plus router, where it is further routed according to the pattern: `/app/page`.  We aren't really routing without `urls.py`; we're adding a second, more important router afterward.  In fact, you can still use the `urls.py` file in the normal Django way because we placed the wildcard at the *end* of the file.  Things like the `/admin/` still work the normal, Django way.

Rather than listing every. single. page. on. your. site. in the `urls.py` file, the router figures out the destination via a convention.  The first url part is taken as the app to go to, and the second url part is taken as the view to call.

For example, the url `/homepage/index/` routes as follows:

* The first url part `homepage` specifies the app that will be used.
* The second url part `index` specifies the view or html page within the app.  In our example:
  * The router first looks for `homepage/views/index.py`.  In this case, it fails because we haven't created it yet.
  * It then looks for `homepage/templates/index.html`.  It finds the file, so it renders the html through the Mako templating engine and returns it to the browser.

The above illustrates the easiest way to show pages: simply place .html files in your templates/ directory.  This is useful for pages that don't have any "work" to do.  Examples might be the "About Us" and "Terms of Service" pages.  There's usually no functionality or permissions issues with these pages, so no view function is required.

> What about the case where a page isn't specified, such as `/homepage/`?  If the url doesn't contain two parts, the router goes to the default page as specified in your settings.py `DEFAULT_PAGE` setting.  This allows you to have a "default page", similar to the way web servers default to the index.html page.  If the path is entirely empty (i.e. http://www.yourserver.com/ with *no* path parts), the router uses both defaults specified in your settings.py file: `DEFAULT_PAGE` and `DEFAULT_APP`.

## Adding a View Function

Let's add some "work" to the process by adding the current server time to the index page.  Create a new file `homepage/views/index.py` and copy this code into it:

```python
from django.conf import settings
from django_mako_plus import view_function
from datetime import datetime
from .. import dmp_render, dmp_render_to_string

@view_function
def process_request(request):
    context = {
        'now': datetime.now(),
    }
    return dmp_render(request, 'index.html', context)
```

Reload your server and browser page, and you should see the exact same page.  It might look the same, but something very important happened in the routing.  Rather than going straight to the `index.html` page, processing went to your new `index.py` file.  At the end of the `process_request` function above, we manually render the `index.html` file.  In other words, we're now doing extra "work" before the rendering.  This is the place to do database connections, modify objects, prepare and handle forms, etc.  It keeps complex code out of your html pages.

Let me pause for a minute and talk about log messages.  If you enabled the logger in the installation, you should see the following in your console:

```
DEBUG controller :: processing: app=homepage, page=index, funcname=, urlparams=['']
DEBUG controller :: calling view function homepage.views.index.process_request
DEBUG controller :: rendering template .../dmp_test/homepage/templates/index.html
```

These debug statements are incredibly helpful in figuring out why pages aren't routing right.  If your page didn't load right, you'll probably see why in these statements.  In my log above, the first line lists what the controller assigned the app and page to be.

The second line tells me the controller found my new `index.py` view, and it called the `process_request` function successfully.  This is important -- the `process_request` function is the "default" view function.  Further, the any web-accessible function must be decorated with `@view_function`.

>This decoration with `@view_function` is done for security.  If the framework let browsers specify any old function, end users could invoke any function of any module on your system!  By requiring the decorator, the framework limits end users to one specifically-named function.

You can have multiple decorators on your function, such as a permissions check and `view_function`:

```python
@view_function
@permission_required('can_vote')
def process_request(request):
    ...
```

> Later in the tutorial, we'll describe another way to call other functions within your view  Even though `process_request` is the default function, you can actually have multiple web-accessible functions within a single .py file.

As stated earlier, we explicitly call the Mako renderer at the end of the `process_request` function.  The context (the third parameter of the call) is a dictionary containing variable names that will be globally available within the template.

Let's use the `now` variable in our index.html template:

```html
<%inherit file="base.htm" />

<%block name="content">
    <div class="content">
      <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
      <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
      <p class="server-time">The current server time is ${ now }.</p>
      <p class="browser-time">The current browser time is...</p>
    </div>
</%block>
```

The `${ varname }` code is Mako syntax and is described more fully on the Mako web site.  Right now, it's most important that you see how to send data from the view to the template.  If you already know Django templates, it's pretty close to the same pattern.  The Django-Mako-Framework tries to improve Django, not entirely change it.

Reload your web page and ensure the new view is working correctly.  You should see the server time printed on the screen.  Each time you reload the page, the time should change.

> You might be wondering about the incomplete sentence under the .browser_time paragraph.  Just hold tight.  We'll be using this later in the tutorial.


#### The Render Functions

> This section explains the two render functions included with DMP.  If you just want to get things working, skip over this section.  You can always come back later for an explanation of how things are put together.

In the example above, we used the `dmp_render` function to render our template.  It's the DMP equivalent of Django's `render` shortcut function.  The primary difference between the two functions (other than, obviously, the names) is DMP's function must be **connected to an app**.  Django searches for templates in a flat list of directories -- while your apps might have templates in them, Django just searches through them in order.  DMP's structure is logically app-based: each of your apps contains a `templates` directory, and DMP always searches the *current* app directly.  With DMP, there are no worries about template name clashes or finding issues.

Because DMP is app-aware, it creates more than one render function -- one per app.    You'll have one version of `dmp_render` in your homepage app, another version of `dmp_render` in your catalog app, and so forth through your apps.  The function is named the same in each module for consistency.

**Practically, you don't need to worry about any of this.  DMP is smart enough to know which render is connected to which app.  You just need to import the function correctly in each of your views.**  In each .py file, use the following import:

```python
# this works in any app/views/*.py file:
from .. import dmp_render, dmp_render_to_string
```

If relative imports (the double dot) bother you, use an absolute one instead:

```python
# this also works in any app/views/*.py file:
from homepage import dmp_render, dmp_render_to_string
```

By using one of the above import lines, you'll always get a template renderer that is app-aware and that processes template inheritance, includes, CSS, and JS files correctly.

> Some Python programmers have strong feelings about relative vs. absolute imports.  They were once strongly discouraged in PEP-8 and other places.  In recent years, Guido and others seem to have softened and suggested that relative imports have a place.  Whatever your flavor of life, pick one of the above.  Personally, I favor the first one (relative importing) because it requires me to think less.

> This tutorial uses the relative import method for a specific reason: view files are often copied across apps.  In my experience, new view files aren't started from scratch very often; instead, programmers copy an existing view, clear it out, and write new functions.  If absolute imports were used (the second method above), the wrong render object would be used when this code line was copied across apps.  Since DMP views are *always* placed in the app/views/ folder, relative imports solve the "copying" issue without any additional problems.  My $0.02.


DMP provides a second function, `dmp_render_to_string`.  Both functions process your template, but `dmp_render_to_string` returns a string rather than an `HttpResponse` object.  If you need a custom response, or if you simply need the rendered string, `dmp_render_to_string` is the ticket.  Most of the time, `dmp_render` is the appropriate method because Django expects the full response object (not just the content string) returned from your views.

For an example of `dmp_render_to_string`, scroll lower in this tutorial to the "Mime Types and Status Codes" section.

If you need to process templates across apps within a single view.py file (likely a rare case), use absolute imports and give an alias to the functions as you import them:

```python
import homepage.dmp_render as homepage_render
import catalog.dmp_render as catalog_render
```

Once you've imported the functions with aliases, simply use the appropriate function for templates in the two apps.

Suppose you need to put your templates in a directory named something other than `/appname/templates/`.  Or perhaps you have a non-traditional app path.  The two above methods are really just convenience methods to make rendering easier.  If you need a custom template instance, switch to the paddle shifters:

```python
from django.conf import settings
from django_mako_plus import view_function
from django_mako_plus.template import get_template_loader
from datetime import datetime

@view_function
def process_request(request):
    context = {
        'now': datetime.now(),
    }

    # this syntax is only needed if you need to customize the way template rendering works
    tlookup = get_template_loader('/app/path/', subdir="my_templates")
    template = tlookup.get_template('index.html')
    return template.render_to_response(request=request, context=context)
```

The above code references an app in a non-standard location and a template subdirectory with a non-standard name.


#### Convenience Functions

You might be wondering: Can I use a dynamically-found app?  What if I need a template object?  Can I render a file directly?

Use the DMP convenience functions to be more dynamic, to interact directly with template objects, or to render a file of your choosing.

*Render a file from any app's template's directory:*

```python
from django_mako_plus import render_template
mystr = render_template(request, 'homepage', 'index.html', context)
```

*Render a file from a custom directory within an app:*

```python
from django_mako_plus import render_template
mystr = render_template(request, 'homepage', 'custom.html', context, subdir="customsubdir")
```

*Render a file at any location, even outside of Django:*

```python
from django_mako_plus import render_template_for_path
mystr = render_template_for_path(request, '/var/some/dir/template.html', context)
```

*Get a template object from an app:*

```python
from django_mako_plus import get_template
template = get_template('homepage', 'index.html')
```

*Get a template object at any location, even outside of Django:*

```python
from django_mako_plus import get_template_for_path
template = get_template_for_path('/var/some/dir/template.html')
```

*Get the real Mako template object:*

```python
from django_mako_plus import get_template_for_path
template = get_template_for_path('/var/some/dir/template.html')
mako_template = template.mako_template
```

See the [Mako documentation](http://www.makotemplates.org/) for more information on working directly with Mako template objects.  Mako has many features that go well beyond the DMP interface.

> The convenience functions are perfectly fine if they suit your needs, but the `dmp_render` function described at the beginning of the tutorial is likely the best choice for most users because it doesn't hard code the app name.  The convenience functions are not Django-API compliant.


#### Can't I Use the Django API?

If you need/want to use the standard Django template API, you can do that too:

```python
from django.shortcuts import render
return render(request, 'homepage/index.html', context)
```

or to be more explicit with Django:

```python
from django.shortcuts import render
return render(request, 'homepage/index.html', context, using='django_mako_plus')
```

Scroll down to [Advanced Topics](#rending-templates-the-standard-way-render) for more information.


## URL Parameters

Django is all about pretty urls.  In keeping with that philosophy, this framework has URL parameters.  We've already used the first two items in the path: the first specifies the app, the second specifies the view/template.  URL parameters are the third part, fourth part, and so on.

In traditional web links, you'd specify parameters using key=value pairs, as in `/homepage/index?first=abc&second=def`.  That's ugly, of course, and it's certainly not the Django way (it does still work, though).

With DMP, you have another, better option available.  You'll specify parameters as `/homepage/index/abc/def/`.  The controller makes them available to your view as `request.urlparams[0]` and `request.urlparams[1]`.

Suppose you have a product detail page that needs the SKU number of the product to display.  A nice way to call that page might be `/catalog/product/142233342/`.  The app=catalog, view=product.py, and urlparams[0]=142233342.

These prettier links are much friendlier when users bookmark them, include them in emails, and write them down.  It's all part of coding a user-friendly web site.

Note that URL parameters don't take the place of form parameters.  You'll still use GET and POST parameters to submit forms.  URL parameters are best used for object ids and other simple items that pages need to display.

Although this might not be the best use of urlparams, suppose we want to display our server time with user-specified format.  On a different page of our site, we might present several different `<a href>` links to the user that contain different formats (we wouldn't expect users to come up with these urls on their own -- we'd create links for the user to click on).  Change your `index.py` file to use a url-specified format for the date:

```python
from django.conf import settings
from django_mako_plus import view_function
from .. import dmp_render, dmp_render_to_string
from datetime import datetime

@view_function
def process_request(request):
    context = {
        'now': datetime.now().strftime(request.urlparams[0] if request.urlparams[0] else '%H:%M'),
    }
    return dmp_render(request, 'index.html', context)
```

The following links now give the time in different formats:

* The default format: `http://localhost:8000/homepage/index/`
* The current hour: `http://localhost:8000/homepage/index/%H/`
* The month, year: `http://localhost:8000/homepage/index/%B,%20%Y`

> If a urlparam doesn't exist, it always returns the empty string ''.  This is slightly different than a regular Python list, which throws an exception when you index it beyond the length of the list.  In DMP, request.urlparams[50] returns the empty string rather than an exception.  The `if` statement in the code above can be used to determine if a urlparam exists or not.  Another way to code a default value for a urlparam is `request.urlparam[2] or 'some default value'`.



## A Bit of Style

Modern web pages are made up of three primary parts: HTML, CSS, and Javascript (media might be a fourth, but we'll go with three for now).  Since all of your pages need these three components, this framework combines them intelligently for you.  All you have to do is name the .html, the css., and the .js file with the same name, and DMP will automatically generate the `<link>` and `<script>` tags for you.  It will even put them in the "right" spot and order in the html (styles at the beginning, scripts at the end).

To style our index.html file, create `homepage/styles/index.css` and copy the following into it:

```python
.server-time {
    font-size: 2em;
    color: red;
}
```

When you refresh your page, the server time should be styled with large, red text.  If you view the html source in your browser, you'll see a new `<link...>` near the top of your file.  It's as easy as naming the files the same and placing the .css file in the styles/ directory.

The framework knows how to follow template inheritance.  For example, since `index.html` extends from `base.htm`, we can actually put our CSS in any of **four** different files: `index.css`, `index.cssm`, `base.css`, and `base.cssm` (the .cssm files are explained in the next section).  Place your CSS styles in the appropriate file, depending on where the HTML elements are located.  For example, let's style our header a little.  Since the `<header>` element is in `base.htm`, create `homepage/styles/base.css` and place the following in it:

```css
html, body {
    margin: 0;
    padding: 0;
}

header {
    padding: 36px 0;
    text-align: center;
    font-size: 2.5em;
    color: #F4F4F4;
    background-color: #0088CC;
}
```

Reload your browser, and you should have a nice white on blue header. If you view source in the browser, you'll see the CSS files were included as follows:

```html
<link rel="stylesheet" type="text/css" href="/static/homepage/styles/base.css?33192040" />
<link rel="stylesheet" type="text/css" href="/static/homepage/styles/index.css?33192040" />
```

Note that `base.css` is included first because it's at the top of the hierarchy.  Styles from `index.css` override any conflicting styles from `base.css`, which makes sense because `index.html` is the final template in the inheritance chain.

> You might be wondering about the big number after the html source `<link>`.  That's the file modification time, in minutes since 1970.  This is included because browsers (especially Chrome) don't automatically download new CSS files.  They use their cached versions until a specified date, often far in the future (this duration is set by your web server). By adding a number to the end of the file, browsers  think the CSS files are "new" because the "filename" changes whenever you change the file.  Trixy browserses...


## A Bit of Style, Reloaded

The style of a web page is often dependent upon the user, such as a user-definable theme in an online email app or a user-settable font family in an online reader.  DMP supports this behavior, mostly because the authors at MyEducator needed it for their online book reader.  You can use Mako (hence, any Python code) not only in your .html files, but also in your CSS and JS files.  Simply name the file with `.cssm` rather than .css.  When the framework sees `index.cssm`, it runs the file through the Mako templating engine before it sends it out.

> Since .cssm files are generated per request, they are embedded directly in the HTML rather than linked.  This circumvents a second call to the server, which would happen every time since the CSS is being dynamically generated.  Dynamic CSS can't be cached by a browser any more than dynamic HTML can.

Let's make the color dynamic by adding a new random variable `timecolor` to our index.py view:

```python
from django.conf import settings
from django_mako_plus import view_function
from .. import dmp_render, dmp_render_to_string
from datetime import datetime
import random

@view_function
def process_request(request):
    context = {
        'now': datetime.now().strftime(request.urlparams[0] if request.urlparams[0] else '%H:%M'),
        'timecolor': random.choice([ 'red', 'blue', 'green', 'brown' ]),
    }
    return dmp_render(request, 'index.html', context)
```

Now, rename your index.css file to `index.cssm`.  Then set the content of index.cssm to the following:

```css
.server-time {
    font-size: 2em;
    color: ${ timecolor };
}
```

Refresh your browser a few times.  Hey look, Ma, the color changes with each refresh!

As shown in the example above, the context dictionary sent the templating engine in `process_request` are globally available in .html, .cssm, and .jsm files.

> Note that this behavior is different than CSS engines like Less and Sass. Most developers use Less and Sass for variables at development time.  These variables are rendered and stripped out before upload to the server, and they become static, normal CSS files on the server.  .cssm files should be used for dynamically-generated, per-request CSS.


## Static and Dynamic Javascript

Javascript files work the same way as CSS files, so if you skipped the two CSS sections above, you might want to go read through them.  This section will be more brief because it's the same pattern again.  Javascript files are placed in the `scripts/` directory, and both static `.js` files and dynamically-created `.jsm` files are supported.

Let's add a client-side, Javascript-based timer.  Create the file `homepage/scripts/index.js` and place the following JQuery code into it:

```javascript
$(function() {
    // update the time every 1 seconds
    window.setInterval(function() {
        $('.browser-time').text('The current browser time is ' + new Date() + '.');
    }, 1000);
});
```

Refresh your browser page, and you should see the browser time updating each second.  Congratulations, you've now got a modern, HTML5 web page.

Let's also do an example of a `.jsm` (dynamic) script.  We'll let the user set the browser time update period through a urlparam.  We'll leave the first parameter alone (the server date format) and use the second parameter to specify this interval.

First, **be sure to change the name of the file from `index.js` to `index.jsm`.**  This tells the framework to run the code through the Mako engine before sending to the browser.  In fact, if you try leaving the .js extension on the file and view the browser source, you'll see the `${ }` Mako code doesn't get rendered.  It just gets included like static html.  Changing the extension to .jsm causes DMP to run Mako and render the code sections.

Update your `homepage/scripts/index.jsm` file to the following:

```javascript
$(function() {
    // update the time every 1 seconds
    window.setInterval(function() {
        $('.browser-time').text('The current browser time is ' + new Date() + '.');
    }, ${ request.urlparams[1] });
});
```

Save the changes and take your browser to [http://localhost:8000/homepage/index/%Y/3000/](http://localhost:8000/homepage/index/%Y/3000/).  Since urlparams[1] is 3000 in this link, you should see the date change every three seconds.  Feel free to try different intervals, but out of concern for the innocent (e.g. your browser), I'd suggest keeping the interval above 200 ms.

> I should note that letting the user set date formats and timer intervals via the browser url are probably not the most wise or secure ideas.  But hopefully, it is illustrative of the capabilities of DMP.


## Minification of JS and CSS

DMP will try to minify your *.js and *.css files using the `rjsmin` and `rcssmin` modules if the settings.py `MINIFY_JS_CSS` is True.  Your Python installation must also have these modules installed

These two modules do fairly simplistic minification using regular expressions.  They are not as full-featured as other minifiers, but they use pure Python code and are incredibly fast.  If you want more complete minification, this probably isn't it.

These two modules might be simplistic, but they *are* fast enough to do minification of dynamic `*.jsm` and `*.cssm` files at production time.  Setting the `MINIFY_JS_CSS` variable to True will not only minify during the `dmp_collectstatic` command, it will minfiy the dynamic files as well as they are rendered for each client.

I've done some informal speed testing with dynamic scripts and styles, and minification doesn't really affect overall template processing speed. YMMV.  Luck favors those that do their own testing.

Again, if you want to disable these minifications procedures, simply set `MINIFY_JS_CSS` to False.

Minification of `*.jsm` and `*.cssm` is skipped during development so you can debug your Javascript and CSS.  Even if your set `MINIFY_JS_CSS` to True, minification only happens when settings.py `DEBUG` is False (at production).



## Ajax Calls

What would the modern web be without Ajax?  Well, truthfully, a lot simpler. :)  In fact, if we reinvented the web with today's requirements, we'd probably end up at a very different place than our current web. Even the name ajax implies the use of xml -- which we don't use much in ajax anymore. Most ajax calls return json or html these days!

But regardless of web history, ajax is required on most pages today.  I'll assume you understand the basics of ajax and focus specifically on the ways this framework supports it.

Suppose we want to reload the server time every few seconds, but we don't want to reload the entire page.  Let's start with the client side of things.  Let's place a refresh button in `homepage/templates/index.html`:

```html
<%inherit file="base.htm" />

<%block name="content">
    <div class="content">
      <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
      <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
      <p class="server-time">The current server time is ${ now }.</p>
      <button id="server-time-button">Refresh Server Time</button>
      <p class="browser-time">The current browser time is .</p>
    </div>
</%block>
```

Note the new `<button>` element in the above html.  Next, we'll add Javascript to the `homepage/scripts/index.jsm` file that runs when the button is clicked:

```javascript
$(function() {
    // update the time every n seconds
    window.setInterval(function() {
        $('.browser-time').text('The current browser time is ' + new Date());
    }, ${ request.urlparams[1] });

    // update server time button
    $('#server-time-button').click(function() {
        $('.server-time').load('/homepage/index_time/');
    });
});
```

The client side is now ready, so let's create the `/homepage/index_time/` server endpoint.  Create a new `homepage/views/index_time.py` file:

```python
from django.conf import settings
from django_mako_plus import view_function
from .. import dmp_render, dmp_render_to_string
from datetime import datetime
import random

@view_function
def process_request(request):
    context = {
        'now': datetime.now(),
    }
    return dmp_render(request, 'index_time.html', context)
```

Finally, create the `/homepage/templates/index_time.html` template, which is rendered at the end of `process_request()` above:

```html
<%inherit file="base_ajax.htm" />

<%block name="content">
    The current server time is ${ now }.
</%block>
```

Note that this template inherits from `base_ajax.htm`.  If you open `base_ajax.htm`, you'll see it doesn't have the normal `<html>`, `<body>`, etc. tags in it.  This supertemplate is meant for snippets of html rather than entire pages.  What it **does** contain is the calls to the `static_renderer` -- the real reason we inherit rather than just have a standalone template snippet.  By calling `static_renderer` in the supertemplate, any CSS or JS files are automatically included with our template snippet.  Styling the ajax response is as easy as creating a `homepage/styles/index_time.css` file.

> We really didn't need to create `index_time.html` at all. Just like in Django, a view function can simply return an `HttpResponse` object.  At the end of the view function, we simply needed to `return HttpResponse('The current server time is %s' % now)`.  The reason I'm rendering a template here is to show the use of `base_ajax.htm`, which automatically includes .css and .js files with the same name as the template.

Reload your browser page and try the button.  It should reload the time *from the server* every time you push the button.

> **Hidden powerup alert!** You can also render a partial template by specifying one of its `<%block>` or `<%def>` tags directly in `render()`.  See [Rendering Partial Templates](#rendering-partial-templates-ajax) for more information.


## Really, a Whole New File for Ajax?

All right, there **is** a shortcut, and a good one at that. The last section showed you how to create an ajax endpoint view.  Since modern web pages have many little ajax calls thoughout their pages, the framework allows you to put several web-accessible methods **in the same .py file**.

Let's get rid of `homepage/views/index_time.py`.  That's right, just delete the file.  Now rename `homepage/templates/index_time.html` to `homepage/templates/index.gettime.html`.  This rename of the html file isn't actually necessary, but it's a nice way to keep the view and template names consistent.

Open `homepage/views/index.py` and add the following to the end of the file:

```python
@view_function
def gettime(request):
    context = {
        'now': datetime.now(),
    }
    return dmp_render(request, 'index.gettime.html', context)
```

Note the function is decorated with `@view_function`, and it contains the function body from our now-deleted `index_time.py`.  The framework recognizes **any** function with this decorator as an available endpoint for urls, not just the hard-coded `process_request` function.  In other words, you can actually name your view methods any way you like, as long as you follow the pattern described in this section.

In this case, getting the server time is essentially "part" of the index page, so it makes sense to put the ajax endpoint right in the same file.  Both `process_request` and `gettime` serve content for the `/homepage/index/` html page.  Having two view files is actually more confusing to a reader of your code because they are so related.   Placing two view functions (that are highly related like these are) in the same file keeps everything together and makes your code more concise and easier to understand.

To take advantage of this new function, let's modify the url in `homepage/scripts/index.jsm`:

```javascript
// update button
$('#server-time-button').click(function() {
    $('.server-time').load('/homepage/index.gettime');
});
```

The url now points to `index.gettime`, which the framework translates to `index.py -> gettime()`.  In other words, a dot (.) gives an exact function within the module to be called rather than the default `process_request` function.

Reload your browser page, and the button should still work.  Press it a few times and check out the magic.

To repeat, a full DMP url is really `/app/view.function/`.  Using `/app/view/` is a shortcut, and the framework translates it as `/app/view.process_request/` internally.

> Since ajax calls often return JSON, XML, or simple text, you often only need to add a function to your view.  At the end of the function, simply `return HttpResponse("json or xml or text")`.  You likely don't need full template, css, or js files.




## Importing Python Modules into Templates

It's easy to import Python modules into your Mako templates.  Simply use a module-level block:

```python
<%!
    import datetime
    from decimal import Decimal
%>
```

or a Python-level block (see the Mako docs for the difference):

```python
<%
    import datetime
    from decimal import Decimal
%>
```

There may be some modules, such as `re` or `decimal` that are so useful you want them available in every template of your site.  In settings.py, add these to the `DEFAULT_TEMPLATE_IMPORTS` variable:

```python
DEFAULT_TEMPLATE_IMPORTS = [
    'import os, os.path, re',
    'from decimal import Decimal',
],
```

Any entries in this list will be automatically included in templates throughout all apps of your site.  With the above imports, you'll be able to use `re` and `Decimal` and `os` and `os.path` anywhere in any .html, .cssm, and .jsm file.

> Whenever you modify the DMP settings, be sure to clean out your cached templates with `python manage.py dmp_cleanup`.  This ensures your compiled templates are rebuilt with the new settings.


## Mime Types and Status Codes

The `dmp_render()` function determines the mime type from the template extension and returns a *200* status code.  What if you need to return JSON, CSV, or a 404 not found?  Just wrap the `dmp_render_to_string` function in a standard Django `HttpResponse` object.  A few examples:

```python
from django.http import HttpResponse

# return CSV
return HttpResponse(dmp_render_to_string(request, 'my_csv.html', {}), mimetype='text/csv')

# return a custom error page
return HttpResponse(dmp_render_to_string(request, 'custom_error_page.html', {}), status=404)
```


## Static Files, Your Web Server, and DMP

Static files are files linked into your html documents like `.css` and `.js` as well as images files like `.png` and `.jpg`.  These are served directly by your web server (Apache, Nginx, etc.) rather than by Django because they don't require any processing.  They are just copied across the Internet.  Serving static files is what web servers were written for, and they are better at it than anything else.

Django-Mako-Plus works with static files the same way that traditional Django does, with one difference: the folder structure is different in DMP.  The folllowing subsections describe how you should use static files with DMP.

> If you read nothing else in this tutorial, be sure to read through the Deployment subsection given shortly.  There's a potential security issue with static files that you need to address before deploying.  Specifically, you need to comment out `BASE_DIR` from the setup shown next.


#### Static File Setup

In your project's settings.py file, be sure you the following:

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    BASE_DIR,
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```

Note that the last line is a serious security issue if you go to production with it.  More on that later.

#### Development

During development, Django will use the `STATICFILES_DIRS` variable to find the files relative to your project root.  You really don't need to do anything special except ensure that the `django.contrib.staticfiles` app is in your list of `INSTALLED_APPS`.  Django's `staticfiles` app is the engine that statics files during development.

Simply place media files for the homepage app in the homepage/media/ folder.  This includes images, videos, PDF files, etc. -- any static files that aren't Javascript or CSS files.

Reference static files using the `${ STATIC_URL }` variable.  For example, reference images in your html pages like this:

```html
<img src="${ STATIC_URL }homepage/media/image.png" />
```

By using the `STATIC_URL` variable from settings in your urls rather than hard-coding the `/static/` directory location, you can change the url to your static files easily in the future.



#### Security at Deployment (VERY Important)

At production/deployment, comment out `BASE_DIR` because it essentially makes your entire project available via your static url (a serious security concern):

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    # BASE_DIR,
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```

When you deploy to a web server, run `dmp_collectstatic` to collect your static files into a separate directory (called `/static/` in the settings above).  You should then point your web server (Apache, Nginx, IIS, etc.) to serve this folder directly to browsers.  For example, in Nginx, you'd set the following:

```
location /static/ {
    alias /path/to/your/project/static/;
    access_log off;
    expires 30d;
}
```

In Apache, you'd set the following:

Alias /static/ /path/to/your/project/static/

```
<Directory /path/to/your/project/static/>
Order deny,allow
Allow from all
</Directory>
```


#### Collecting Static Files

DMP comes with a manage.py command `dmp_collectstatic` that copies all your static resource files into a single subtree so you can easily place them on your web server.  At development, your static files reside within the apps they support.  For example, the `homepage/media` directory is a sibling to `homepage/views` and `/homepage/templates`.  This combined layout makes for nice development, but a split layout is more optimal for deployment because you have two web servers active at deployment (a traditional server like Apache doing the static files and a Python server doing the dynamic files).

The Django-Mako-Plus framework has a different layout than traditional Django, so it comes with its own static collection command.  When you are ready to publish your web site, run the following to split out the static files into a single subtree:

```python
python3 manage.py dmp_collectstatic
```

This command will copy of the static directories--`/media/`, `/scripts/`, and `/styles/`--to a common subtree called `/static/` (or whatever `STATIC_ROOT` is set to in your settings).  Everything in these directories is copied (except dynamic `*.jsm/*.cssm` files, which aren't static).

> Since this new `/static/` directory tree doesn't contain any of your templates, views, settings, or other files, you can make the entire subtree available via your web server.  This gives you the best combination of speed and security and is the whole point of this exercise.

The `dmp_collectstatic` command has the following command-line options:

* The commmand will refuse to overwrite an existing `/static/` directory.  If you already have this directory (either from an earlier run or for another purpose), you can 1) delete it before collecting static files, or 2) specify the overwrite option as follows:

```
python3 manage.py dmp_collectstatic --overwrite
```

* If you need to ignore certain directories or filenames, specify them with the `--ignore` option.  This can be specified more than once, and it accepts Unix-style wildcards:

```
python3 manage.py dmp_collectstatic --ignore=.cached_templates --ignore=fixtures --ignore=*.txt
```


##### Django Apps + DMP Apps

You might have some traditional Django apps (like the built-in `/admin` app) and some DMP apps (like our `/homepage` in this tutorial).  Your Django apps need the regular `collectstatic` routine, and your DMP apps need the `dmp_collectstatic` routine.

The solution is to run both commands.  Using the options of the two commands, you can either send the output from each command to *two different* static directories, or you can send them to a single directory and let the files from the second command potentially overwrite the files from the first.  I suggest this second method:

```
python3 manage.py collectstatic
python3 manage.py dmp_collectstatic --overwrite
```
The above two commands will use both methods to bring files into your `/static/` folder.  You might get some duplication of files, but the output of the commands are different enough that it should work without issues.



## Redirecting

Redirecting the browser is common in today's sites.  For example, during form submissions, web applications often redirect the browser to the *same* page after a form submission (and handling with a view)--effectively switching the browser from its current POST to a regular GET.  If the user hits the refresh button within his or her browser, the page simply gets refreshed without the form being submitted again. It prevents users from being confused when the browser opens a popup asking if the post data should be submitted again.

DMP provides a Javascript-based redirect response and four exception-based redirects.  The first, `HttpResponseJavascriptRedirect`, sends a regular HTTP 200 OK response that contains Javascript to redirect the browser: `<script>window.location.href="...";</script>`.  Normally, redirecting should be done via Django's built-in `HttpResponseRedirect` (HTTP 302), but there are times when a normal 302 doesn't do what you need.  For example, suppose you need to redirect the top-level page from an Ajax response.  Ajax redirects normally only redirects the Ajax itself (not the page that initiated the call), and this default behavior is usually what is needed.  However, there are instances when the entire page must be redirected, even if the call is Ajax-based.  Note that this class doesn't use the <meta> tag or Refresh header method because they aren't predictable within Ajax (for example, JQuery seems to ignore them).

The four exception-based redirects allow you to raise a redirect from anywhere in your code.  For example, the user might not be authenticated correctly, but the code that checks for this can't return a response object.  Since these three are exceptions, they bubble all the way up the call stack to the DMP router -- where they generate a redirect to the browser.  Exception-based redirects should be used sparingly, but they can help you create clean code.  For example, without the ability to redirect with an exception, you might have to pass and return other variables (often the request/response objects) through many more function calls.

As you might expect, `RedirectException` sends a normal 302 redirect and `PermanentRedirectException` sends a permanent 301 redirect.  `JavascriptRedirectException` sends a redirect `HttpResponseJavascriptRedirect` as described above.

The fourth exception, `InternalRedirectException`, is simpler and faster: it restarts the routing process with a different view/template within the *current* request, without changing the browser url.  Internal redirect exceptions are rare and shouldn't be abused. An example might be returning an "upgrade your browser" page to a client; since the user has an old browser, a regular 302 redirect might not work the way you expect.  Redirecting internally is much safer because your server stays in control the entire time.

The following code shows examples of different methods if redirection:

```python
from django.http import HttpResponseRedirect
from django_mako_plus import HttpResponseJavascriptRedirect
from django_mako_plus import RedirectException, PermanentRedirectException, JavascriptRedirectException, InternalRedirectException

# return a normal redirect with Django from a process_request method
return HttpResponseRedirect('/some/new/url/')

# return a Javascript-based redirect from a process_request method
return HttpResponseJavascriptRedirect('/some/new/url/')

# raise a normal redirect from anywhere in your code
raise RedirectException('/some/new/url')

# raise a permanent redirect from anywhere in your code
raise PermanentRedirectException('/some/new/url')

# raise a Javascript-based redirect from anywhere in your code
raise JavascriptRedirectException('/some/new/url')

# restart the routing process with a new view without returning to the browser.
# the browser keeps the same url and doesn't know a redirect has happened.
# the request.dmp_router_module and request.dmp_router_function variables are updated
# to reflect the new values, but all other variables, such as request.urlparams,
# request.GET, and request.POST remain the same as before.
# the next line is as if the browser went to /homepage/upgrade/
raise InternalRedirectException('homepage.views.upgrade', 'process_request')
```

DMP adds a custom header, "Redirect-Exception", to all exception-based redirects.  Although you'll probably ignore this most of the time, the header allows you to further act on exception redirects in response middleware, your web server, or calling Javascript code.

> Is this an abuse of exceptions?  Probably.  But from one viewpoint, a redirect can be seen as an exception to normal processing.  It is quite handy to be able to redirect the browser from anywhere in your codebase.  If this feels dirty to you, feel free to skip it.


# Deployment Recommendations

This section has nothing to do with the Django-Mako-Framework, but I want to address a couple issues in hopes that it will save you some headaches.  One of the most difficult decisions in Django development is deciding how to deploy your system.  In particular, there are several ways to connect Django to your web server: mod_wsgi, FastCGI, etc.

At MyEducator, we've been through all of them at various levels of testing and production.  By far, we've had the best success with [uWSGI](http://docs.djangoproject.com/en/dev/howto/deployment/wsgi/uwsgi/).  It is a professional server, and it is stable.

One other decision you'll have to make is which database use.  I'm excluding the "big and beefies" like Oracle or DB2.  Those with sites that need these databases already know who they are.  Most of you will be choosing between MySQL, PostgreSQL, and perhaps another mid-level database.

In choosing databases, you'll find that many, if not most, of the Django developers use PostgreSQL.  The system is likely tested best and first on PG.  We started on MySQL, and we moved to PG after experiencing a few problems.  Since deploying on PG, things have been amazingly smooth.

Your mileage may vary with everything in this section.  Do your own testing and take it all as advice only.  Best of luck.

## Deployment Tutorials

The following links contain tutorials for deploying Django with DMP:

* http://blog.tworivershosting.com/2014/11/ubuntu-server-setup-for-django-mako-plus.html


# Advanced Topics

The following sections are for those who want to take advantage of some extra, but likely less used, features of DMP.


## Useful Variables

At the beginning of each request (as part of its middleware), DMP adds a number of fields to the request object.  These
variables primarily support the inner workings of the DMP router, but they may be useful to you as well.  The following
are available throughout the request:

* `request.dmp_router_app`: The Django application specified in the URL.  In the URL `http://www.server.com/calculator/index/1/2/3`, the `dmp_router_app` is the string "calculator".
* `request.dmp_router_page`: The name of the Python module specified in the URL.  In the URL `http://www.server.com/calculator/index/1/2/3`, the `dmp_router_page` is the string "index".  In the URL `http://www.server.com/calculator/index.somefunc/1/2/3`, the `dmp_router_page` is still the string "index".
* `request.dmp_router_function`: The name of the function within the module that will be called, even if it is not specified in the URL.  In the URL `http://www.server.com/calculator/index/1/2/3`, the `dmp_router_function` is the string "process_request" (the default function).  In the URL `http://www.server.com/calculator/index.somefunc/1/2/3`, the `dmp_router_page` is the string "somefunc".
* `request.dmp_router_module`: The name of the real Python module specified in the URL, as it will be imported into the runtime module space.  In the URL `http://www.server.com/calculator/index/1/2/3`, the `dmp_router_module` is the string "calculator.views.index".
* `request.dmp_router_class`: The name of the class if the router sees that the "function" is actually a class-based view.  None otherwise.
* `request.urlparams`: A list of parameters specified in the URL.  See the section entitled "URL Parameters" above for more information.
* `request.dmp_router_callback`: The view callable (function, method, etc.) to be called by the router.  Of all the variables listed here, this is the one that the router actually uses directly to make the view call.  The other variables are only used to get a reference to this callback.



## Customize the URL Pattern

Suppose your project requires a different URL pattern than the normal `/app/page/param1/param2/...`.  For example, you might need the user id in between the app and page: `/app/userid/page/param1/param1...`.   This is supported in two different ways.

#### URL Patterns: Take 1

The first method is done with named parameters, and it is the "normal" way to customize the url pattern.  Instead of including the default`django_mako_plus.urls` module in your `urls.py` file, you can instead create the patterns manually.  Start with the [patterns in the DMP source](http://github.com/doconix/django-mako-plus/blob/master/django_mako_plus/urls.py) and modify them as needed.

The following is one of the URL patterns, modified to include the `userid` parameter in between the app and page:

```
from django_mako_plus import route_request
urlpatterns = [
    ...
    url(r'^(?P<dmp_router_app>[_a-zA-Z0-9\.\-]+)/(?P<userid>\d+)/(?P<dmp_router_page>[_a-zA-Z0-9\.\-]+)/?(?P<urlparams>.*)$', route_request, name='DMP - /app/page'),
    ...
]
```

Then, in your process_request method, be sure to include the userid parameter.  This is according to the standard Django documentation with named parameters:

```
@view_function
def process_request(request, userid):
    ...
```

DMP doesn't use the positional index of the arguments, so you can rearrange patterns as needed. However, you must use named parameters for both DMP and your custom parameters (Django doesn't allow both named and positional parameters in a single pattern).

You can also "hard code" the app or page name in a given pattern.  Suppose you want urls entirely made of numbers (without any slashes) to go the user app:  `/user/views/account.py`.  The pattern would hard code the app and page as [extra options](http://docs.djangoproject.com/en/1.10/topics/http/urls/#passing-extra-options-to-view-functions).  In urls.py:

```python
from django_mako_plus import route_request
urlpatterns = [
    ...
    url(r'^(?P<userid>\d+)$', route_request, { 'dmp_router_app': 'user', 'dmp_router_page': 'account' }, name='User Account'),
    ...
]
```

Use the following named parameters in your patterns to tell DMP which app, page, and function to call:

* `(?P<dmp_router_app>[_a-zA-Z0-9\-]+)` is the app name.  If omitted, it is set to `DEFAULT_APP` in settings.
* `(?P<dmp_router_page>[_a-zA-Z0-9\-]+)` is the view module name.  If omitted, it is set to `DEFAULT_APP` in settings.
* `(?P<dmp_router_function>[_a-zA-Z0-9\.\-]+)` is the function name.  If omitted, it is set to `process_request`.
* `(?P<urlparams>.*)` is the url parameters, and it should normally span multiple slashes.  The default patterns set this value to anything after the page name.  This value is split on the slash `/` to form the `request.urlparams` list.  If omitted, it is set to the empty list `[]`.

#### URL Patterns: Take 2

The second method is done by directly modifying the variables created in the middleware.  This can be done through a custom middleware view function that runs after `django_mako_plus.RequestInitMiddleware` (or alternatively, you could create an extension to this class and replace the class in the `MIDDLEWARE` list).

Once `RequestInitMiddleware.process_view` creates the variables, your custom middleware can modify them in any way.  As view middleware, your function will run *after* the DMP middleware by *before* routing takes place in `route_request`.

This method of modifying the URL pattern allows total freedom since you can use python code directly.  However, it would probably be done in an exceptional rather than typical case.


## CSRF Tokens

In support of the Django CSRF capability, DMP includes `csrf_token` and `csrf_input` in the context of every template.  Following [Django's lead](https://docs.djangoproject.com/en/dev/ref/csrf/), this token is always available and cannot be disabled for security reasons.

However, slightly different than Django's default templates (but following [Jinja2's lead](https://docs.djangoproject.com/en/dev/ref/csrf/#using-csrf-in-jinja2-templates)), use `csrf_input` to render the CSRF input:

```
<form action="" method="post">
    ${ csrf_input }
    ...
</form>
```
> Since the CSRF token requires a request object, using an empty request `dmp_render(None, ...)` prevents the token from being included in your templates.


## Behind the CSS and JS Curtain

After reading about automatic CSS and JS inclusion, you might want to know how it works.  It's all done in the templates (base.htm now, and base_ajax.htm in a later section below) you are inheriting from.  Open `base.htm` and look at the following code:

```
## render the styles with the same name as this template and its supertemplates
${ django_mako_plus.link_css(self) }

...

## render the scripts with the same name as this template and its supertemplates
${ django_mako_plus.link_js(self) }
```

The  two calls, `link_css()` and `link_js()`, include the `<link>` and `<script>` tags for the template name and all of its supertemplates.  The CSS should be linked near the top of your file (`<head>` section), and the JS should be linked near the end (per best practices).

This all works because the `index.html` template extends from the `base.htm` template.  If you fail to inherit from `base.htm` or `base_ajax.htm`, DMP won't be able to include the support files.


## Using Django and Jinja2 Tags and Syntax

In most cases, third-party functionality can be called directly from Mako.  For example, use the [Django Paypal](http://django-paypal.readthedocs.io/) form by converting the Django syntax to Mako:

* The docs show: `{{ form.render }}`
* You use:`${ form.render() }`

In other words, use regular Python in DMP to call the tags and functions within the third party library.  For example, you can render a [Crispy Form](http://django-crispy-forms.readthedocs.io/) by importing and calling its `render_crispy_form` function right within your template.

For example, suppose your view constructs a Django form, which is then sent to your template via the context dictionary.  Your template would look like this:

```
<%! from crispy_forms.utils import render_crispy_form %>

<html>
<body>
    <form method="POST">
        ${ csrf_input }
        ${ render_crispy_form(form) }
    </form>
</body>
</html>
```

If you call the `render_crispy_form` method in many templates, you may want to add the import to `DEFAULT_TEMPLATE_IMPORTS` in your `settings.py` file.  Once this import exists in your settings, the function will be globally available in every template on your site.

> Whenever you modify the DMP settings, be sure to clean out your cached templates with `python manage.py dmp_cleanup`.  This ensures your compiled templates are rebuilt with the new settings.

However, there may be times when you need or want to call real, Django tags.  For example, although [Crispy Forms'](http://django-crispy-forms.readthedocs.io/) functions can be called directly, you may want to use its custom tags.

To enable alternative syntaxes, uncomment (or add) the following to your `settings.py` file:

```python
'DEFAULT_TEMPLATE_IMPORTS': [
    'from django_mako_plus import django_syntax, jinja2_syntax, alternate_syntax
],
```

Then clear out the compiled templates caches:

```
python manage.py dmp_cleanup
```

Now that the functions are imported, you can include a Django expression or embed an entire block within your Mako template by using a filter:

```
## Expression containing Django template syntax (assuming name was created in the view.py)
${ '{{ name }}' | django_syntax(context) }

## Full Django code block, with Mako creating the variable first
<% titles = [ 'First', 'Second', 'Third' ] %>
<%block filter="django_syntax(context, titles=titles)">
    {% for title in titles %}
        <h2>
            {{ title|upper }}
        </h2>
    {% endfor %}
</%block>

## Third-party, crispy form tags (assume my_formset was created in the view.py)
<%block filter="django_syntax(context)">
    {% load crispy_forms_tags %}
    <form method="post" class="uniForm">
        {{ my_formset|crispy }}
    </form>
</%block>
```

The `context` parameter passes your context variables to the Django render call.  It is a global Mako variable (available in any template), and it is always included in the filter.  In other words, include `context` every time as shown in the examples above.

#### Jinja2, Mustache, Cheetah, and ((insert template engine)).

If Jinja2 is needed, replace the filter with `jinja2_syntax(context)` in the above examples.  If another engine is needed, replace the filter with `template_syntax(context, 'engine name')` as specified in `settings.TEMPLATES`.  DMP will render with the appriate engine and put the result in your HTML page.

#### Local Variables

Embedded template code has access to any variable passed to your temple (i.e. any variable in the context).  Although not an encouraged practice, variables are sometimes created right in your template, and faithful to the Mako way, are not accessible in embedded blocks.

You can pass locally-created variables as kwargs in the filter call.  This is done with `titles=titles` in the Django code block example above.



## Rending Templates the Standard Way: `render()`

If you prefer using the standard Django `render()` methods, as described in the Django tutorial, DMP is behind you all the way.  The code below is now sans the `dmp_render` function; it instead sports the regular `render` method from the shortcuts module:

```python
from django.conf import settings
from django.shortcuts import render
from django_mako_plus import view_function
from datetime import datetime

@view_function
def process_request(request):
    context = {
        'now': datetime.now(),
    }
    return render(request, 'homepage/index.html', context)
    # or
    return render(request, 'homepage/index.html', context, using='django_mako_plus')
```

However, *be sure to note one specific requirement* when using the normal Django methods.  You must specify your template with the `app/template.html` format.  Since the DMP engine is specific to your apps, it needs to know which app your template resides in.

The the second version of the `render` call in the example above includes the `using` parameter, which specifically tells Django to use the DMP engine for rendering.  If you omit this, Django starts with the first template engine listed in your settings.py, which may or may not be DMP.  If DMP is the only engine listed, there's no reason to specify the `using` parameter.  This confusion is explained in detail in the Django documentation.

The following is another example of using the standard Django methods.  Note the app/template format in the filename again:

```python
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from django_mako_plus import view_function
from datetime import datetime

@view_function
def process_request(request):
    context = {
      'now': datetime.now(),
    }
    template = get_template('homepage/index.html')
    # or
    template = get_template('homepage/index.html', using='django_mako_plus')
    return HttpResponse(template.render(context=context, request=request))
```


As you can hopefully see, DMP provides custom functions like `dmp_render` and also allows regular Django functions.  Use whichever best suits your needs.


## Rendering Partial Templates (Ajax!)

One of the hidden features of Mako is its ability to render individual blocks of a template, and this feature can be used to make reloading parts of a page quick and easy.  Are you thinking Ajax here?  The trick is done by specifying the `def_name` parameters in `render()`.  You may want to start by reading about `<%block>` and `<%def>` tags in the [Mako documentation](http://docs.makotemplates.org/en/latest/defs.html).

Suppose you have the following template, view, and JS files:

**`index.html`** with a `server_time` block:

```html
<%inherit file="base.htm" />

<%block name="content">
    <div class="content">
      <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
      <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
      <p class="server-time">
          <%block name="server_time">
             The current server time is ${ now }.
          </%block>
      </p>
      <button id="server-time-button">Refresh Server Time</button>
      <p class="browser-time">The current browser time is .</p>
    </div>
</%block>
```

**`index.py`** with an `if` statement and two `dmp_render` calls:

```python
from django.conf import settings
from django_mako_plus import view_function
from .. import dmp_render, dmp_render_to_string
from datetime import datetime
import random

@view_function
def process_request(request):
    context = {
        'now': datetime.now().strftime('%H:%M'),
    }
    if request.urlparams[0] == 'gettime':
        return dmp_render(request, 'index.html', context, def_name='server_time')
    return dmp_render(request, 'index.html', context)
```

**`index.js`**:

```javascript
// update button
$('#server-time-button').click(function() {
    $('.server-time').load('/homepage/index/gettime/');
});
```

On initial page load, the `if request.urlparams[0] == 'gettime':` statement is false, so the full `index.html` file is rendered.  However, when the update button's click event is run, the statement is **true** because `/gettime` is added as the first url parameter.  This is just one way to switch the `dmp_render` call.  We could also have used a regular CGI parameter, request method (GET or POST), or any other way to perform the logic.

When the `if` statement goes **true**, DMP renders the `server_time` block of the template instead of the entire template.  This corresponds nicely to the way the Ajax call was made: `$('.server-time').load()`.

**Partial templates rock because:**

1. We serve both the initial page *and* the Ajax call with the same code.  Write once, debug once, maintain once.  Single templates, FTW!
2. The same logic, `index.py`, is run for both the initial call and the Ajax call.  While this example is really simplistic, more complex views may have significant work to do (form handling, table creation, object retrieval) before the page or the Ajax can be rendered.
3. By splitting the template into many different blocks, a single view/template can serve many different Ajax calls throughout the page.

> Note that, in the Ajax call, your view will likely perform more logic than is needed (i.e. generate data for the parts of the template outside the block that won't be rendered).  Often, this additional processing is minimal and is outweighed by the benefits above.  When additional processing is not desirable, simply create new `@view_function` functions, one for each Ajax call.  You can still use the single template by having the Ajax endpoints render specific blocks.

**Variable Scope**

The tricky part of block rendering is ensuring your variables are accessible.  You can read more about namespaces on the Mako web site, but here's the tl;dr version:

* Variables sent from the view in the context dictionary are available throughout the page, regardless of the block.  If your variables are part of the context, you're golden.
* Variables created within your template but **outside the block** have to be explicitly defined in the block declaration.  This is a Mako thing, and it's a consequence of the way Mako turns blocks and defs into Python methods.  If you need a variable defined outside a block, be sure to define your template with a comma-separated list of `args`.  Again, [the Mako documentation](http://docs.makotemplates.org/en/latest/namespaces.html) gives more information on these fine details.

**`index.html`** with a `counter` variable defined in the template:

```html
<%inherit file="base.htm" />

<%block name="content">
    <div class="content">
      <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
      <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
      %for counter in range(10):
          <p class="server-time">
              <%block name="server_time" args="counter">
                 ${ counter }: The current server time is ${ now }.
              </%block>
          </p>
      %endfor
      <button id="server-time-button">Refresh Server Time</button>
      <p class="browser-time">The current browser time is .</p>
    </div>
</%block>
```

Since `counter` won't get defined when `def_name='server_time'`, **`index.py`** must add it to the `context` (but only for the Ajax-oriented `dmp_render` function):

```python
from django.conf import settings
from django_mako_plus import view_function
from .. import dmp_render, dmp_render_to_string
from datetime import datetime
import random

@view_function
def process_request(request):
    context = {
        'now': datetime.now().strftime('%H:%M:%S'),
    }
    if request.urlparams[0] == 'gettime':
        context['counter'] = 100
        return dmp_render(request, 'index.html', context, def_name='server_time')
    return dmp_render(request, 'index.html', context)
```


## Sass Integration

DMP can automatically compile your .scss files each time you update them.  When a template is rendered the first time, DMP checks the timestamps on the .scss file and .css file, and it reruns Sass when necessary.  Just be sure to set the `SCSS_BINARY` option in settings.py.

When `DEBUG = True`, DMP checks the timestamps every time a template is rendered.  When in production mode (`DEBUG = False`), DMP only checks the timestamps the first time a template is rendered -- you'll have to restart your server to recompile updated .scss files.  You can disable Sass integration by removing the `SCSS_BINARY` from the settings or by setting it to `None`.

Note that `SCSS_BINARY` *must be specified in a list*.  DMP uses Python's subprocess.Popen command without the shell option (it's more cross-platform that way, and it works better with spaces in your paths).  Specify any arguments in the list as well.  For example, the following settings are all valid:

```
'SCSS_BINARY': [ 'scss' ],
# or:
'SCSS_BINARY': [ 'C:\\Ruby200-x64\\bin\\scss' ],
# or:
'SCSS_BINARY': [ '/usr/bin/env', 'scss', '--unix-newlines', '--cache-location', '/tmp/' ],
# or, to disable:
'SCSS_BINARY': None,
```

If Sass isn't running right, check the DMP log statements.  When the log is enabled, it shows the exact command syntax that DMP is using.  Copy and paste the code into a terminal and troubleshoot the command manually.

> You might be wondering if DMP supports `.scssm` files (Mako embedded in Sass files).  Through a bit of hacking the process, it's a qualified Yes!  Consider `.scssm` support as beta right now.  Only Mako expressions are working thus far: `${ ... }`.  Any other Mako constructs get stripped out by the compiler.


## Class-Based Views

Django-Mako-Plus supports Django's class-based view concept.  You can read more about this pattern in the Django documentation.  If you are using view classes, DMP automatically detects and adjusts accordingly.  If you are using regular function-based views, skip this section for now.

With DMP, your class-based view will be discovered via request url, so you have to name your class accordingly.  In keeping with the rest of DMP, the default class name in a file should be named `class process_request()`.  Consider the following `index.py` file:

```python
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from .. import dmp_render, dmp_render_to_string
from datetime import datetime

class process_request(View):
    def get(self, request):
        context = {
            'now': datetime.now().strftime(request.urlparams[0] if request.urlparams[0] else '%H:%M'),
        }
        return dmp_render(request, 'index.html', context)

class discovery_section(View):
    def get(self, request):
        return HttpResponse('Get was called.')

    def post(self, request):
        return HttpResponse('Post was called.')
```

In the above `index.py` file, two class-based views are defined.  The first is called with the url `/homepage/index/`.  The second is called with the url `/homepage/index.discovery_section/`.

In contrast with normal function-based routing, class-based views do not require the `@view_function` decorator, which provides security on which functions are web-accessible.  Since class-based views must extend django.views.generic.View, the security provided by the decorator is already provided.  DMP assumes that **any extension of View will be accessible**.

> Python programmers usually use TitleCaseClassName (capitalized words) for class names.  In the above classes, I'm instead using all lowercase (which is the style for function and variable names) so my URL doesn't have uppercase characters in it.  If you'd rather use TitleCaseClassName, such as `class DiscoverySection`, be sure your URL matches it, such as `http://yourserver.com/homepage/index.DiscoverySection/`.


## Templates Located Elsewhere

This impacts few users of DMP, so you may want to skip this section for now.

Suppose your templates are located in a directory outside your normal project root.  For whatever reason, you don't want to put your templates in the app/templates directory.


#### Case 1: Templates Within Your Project Directory

If the templates you need to access are within your project directory, no extra setup is required.  Simply reference those templates relative to the root project directory.  For example, to access a template located at BASE_DIR/homepage/mytemplates/sub1/page.html, use the following:

```python
return dmp_render(request, '/homepage/mytemplates/sub1/page.html', context)
```

Note the starting slash on the path.  That tells DMP to start searching at your project root.

Don't confuse the slashes in the above call with the slash used in Django's `render` function.  When you call `render`, the slash separates the app and filename.  The above call uses `dmp_render`, which is a different function.  You should really standardize on one or the other throughout your project.


#### Case 2: Templates Outside Your Project Directory

Suppose your templates are located on a different disk or entirely different directory from your project.  DMP allows you to add extra directories to the template search path through the `TEMPLATES_DIRS` setting.  This setting contains a list of directories that are searched by DMP regardless of the app being referenced.  To include the `/var/templates/` directory in the search path, set this variable as follows:

```python
'TEMPLATES_DIRS': [
   '/var/templates/',
],
```

Suppose, after making the above change, you need to render the '/var/templates/page1.html' template:

```python
return dmp_render(request, 'page1.html', context)
```

DMP will first search the current app's `templates` directory (i.e. the normal way), then it will search the `TEMPLATES_DIRS` list, which in this case contains `/var/templates/`.  Your `page1.html` template will be found and rendered.


## Template Inheritance Across Apps

You may have noticed that this tutorial has focused on a single app.  Most projects consist of many apps.  For example, a sales site might have an app for user management, an app for product management, and an app for the catalog and sales/shopping-cart experience.  All of these apps probably want the same look and feel, and all of them likely want to extend from the **same** `base.htm` file.

When you run `python3 manage.py dmp_startapp <appname>`, you get **new** `base.htm` and `base_ajax.htm` files each time.  This is done to get you started on your first app.  On your second, third, and subsequent apps, you probably want to delete these starter files and instead extend your templates from the `base.htm` and `base_ajax.htm` files in your first app.

In fact, in my projects, I usually create an app called `base_app` that contains the common `base.htm` html code, site-wide CSS, and site-wide Javascript.  Subsequent apps simply extend from `/base_app/templates/base.htm`.  The common `base_app` doesn't really have end-user templates in it -- they are just supertemplates that support other, public apps.

DMP supports cross-app inheritance by including your project root (e.g. `settings.BASE_DIR`) in the template lookup path.  All you need to do is use the full path (relative to the project root) to the template in the inherits statement.

Suppose I have the following app structure:

```
dmptest
    base_app/
        __init__.py
        media/
        scripts/
        styles/
        templates/
            site_base_ajax.htm
            site_base.htm
        views/
            __init__.py
    homepage/
        __init__.py
        media/
        scripts/
        styles/
        templates/
            index.html
        views/
            __init__.py
```

I want `homepage/templates/index.html` to extend from `base_app/templates/site_base.htm`.  The following code in `index.html` sets up the inheritance:

```html
        <%inherit file="/base_app/templates/site_base.htm" />
```

Again, the front slash in the name above tells DMP to start the lookup at the project root.

> In fact, my pages are often three inheritance levels deep: `base_app/templates/site_base.htm -> homepage/templates/base.htm -> homepage/templates/index.html` to provide for site-wide page code, app-wide page code, and specific page code.


## DMP Signals

DMP sends several custom signals through the Django signal dispatcher.  The purpose is to allow you to hook into the router's processing.  Perhaps you need to run code at various points in the process, or perhaps you need to change the request.dmp_* variables to modify the router processing.

Before going further with this section's examples, be sure to read the standard Django signal documentation.  DMP signals are simply additional signals in the same dispatching system, so the following examples should be easy to understand once you know how Django dispatches signals.

#### Step 1: Enable DMP Signals

Be sure your settings.py file has the following in it:

```
'SIGNALS': True,
```
#### Step 2: Create a Signal Receiver

The following creates two receivers.  The first is called just before the view's process_request function is called.  The second is called just before DMP renders .html templates.

```python
from django.dispatch import receiver
from django_mako_plus import signals

@receiver(signals.dmp_signal_pre_process_request)
def dmp_signal_pre_process_request(sender, **kwargs):
    request = kwargs['request']
    print('>>> process_request signal received!')

@receiver(signals.dmp_signal_pre_render_template)
def dmp_signal_pre_render_template(sender, **kwargs):
    request = kwargs['request']
    context = kwargs['context']            # the template variables
    template = kwargs['template']          # the Mako template object that will do the rendering
    print('>>> render_template signal received!')
    # let's return a different template to be used - DMP will use this instead of kwargs['template']
    tlookup = get_template_loader('myapp')
    template = tlookup.get_template('different.html')
```

The above code should be in a code file that is called during Django initialization.  Good locations might be in a `models.py` file or your app's `__init__.py` file.

See the `django_mako_plus/signals.py` file for all the available signals you can listen for.

## Translation (Internationalization)


If your site needs to be translated into other languages, this section is for you.  I'm sure you are aware that Django has full support for translation to other languages.  If not, you should first read the standard Translation documentation at http://docs.djangoproject.com/en/dev/topics/i18n/translation/.

DMP supports Django's translation functions--with one caveat.  Since Django doesn't know about Mako, it can't translate strings in your Mako files.  DMP fixes this with the `dmp_makemessages` command.  Instead of running `python3 manage.py makemessages` like the Django tutorial shows, run `python3 manage.py dmp_makemessages`.  Since the DMP version is an extension of the standard version, the same command line options apply to both.

> IMPORTANT: Django ignores hidden directories when creating a translation file.  Most DMP users keep compiled templates in the hidden directory `.cached_templates`.  The directory is hidden on Unix because it starts with a period.  If your cached templates are in hidden directories, be sure to run the command with `--no-default-ignore`, which allows hidden directories to be searched.

> Internally, `dmp_makemessages` literally extends the `makemessages` class.  Since Mako templates are compiled into .py files at runtime (which makes them discoverable by `makemessages`), the DMP version of the command simply finds all your templates, compiles them, and calls the standard command.  Django finds your translatable strings within the cached_templates directory (which holds the compiled Mako templates).

Suppose you have a template with a header you want translated.  Simply use the following in your template:

```html
<%! from django.utils.translation import ugettext as _ %>
<p>${ _("World History") }</p>
```

Run the following at the command line:

```
python3 manage.py dmp_makemessages --no-default-ignore
```

Assuming you have translations set up the way Django's documentation tells you to, you'll get a new language.po file.  Edit this file and add the translation.  Then compile your translations:

```
python3 manage.py compilemessages
```

Your translation file (language.mo) is now ready, and assuming you've set the language in your session, you'll now see the translations in your template.

> FYI, the `dmp_makemessages` command does everything the regular command does, so it will also find translatable strings in your regular view files as well.  You don't need to run both `dmp_makemessages` and `makemessages`


## Cleaning Up

DMP caches its compiled templates in subdirectories of each app.  The default locations for each app are `app/templates/.cached_templates`, `app/scripts/.cached_templates`, and `app/styles/.cached_templates`, although the exact name depends on your settings.py.  Normally, these cache directories are hidden and warrant your utmost apathy.  However, there are times when DMP fails to update a cached template as it should.  Or you might just need a pristine project without these generated files.  This can be done with a Unix find command or through DMP's `dmp_cleanup` management command:

```
# see what would be be done without actually deleting any cache folders
python manage.py dmp_cleanup --trial-run

# really delete the folders
python manage.py dmp_cleanup
```

Sass also generates compiled files that you can safely remove.  When you create a .scss file, Sass generates two additional files: `.css` and `.css.map`.  If you later remove the .scss, you leave the two generated, now orphaned, files in your `styles` directory.  While some editors remove these files automatically, you can also remove them through DMP's `dmp_sass_cleanup` management command:

```
# see what would be be done without actually deleting anything
python manage.py dmp_sass_cleanup --trial-run

# really delete the files
python manage.py dmp_sass_cleanup
```

With both of these management commands, add `--verbose` to the command to include messages about skipped files, and add `--quiet` to silence all messages (except errors).

> You might be wondering how DMP knows whether a file is a regular .css or a Sass-generated one.  It looks in your .css files for a line starting with `/*# sourceMappingURL=yourtemplate.css.map */`.  When it sees this marker, it decides that the file was generated by Sass and can be deleted if the matching .scss file doesn't exist.  Any .css files that omit this marker are skipped.


## Getting to Static Files Via Fake Templates

You might be wondering who came up with the heading of this section.  Fake Templates?  Let me explain.  No, there is too much.  Let me sum up:  In rare use cases, you may want to take advantage of DMP's static files
capability, even though you aren't rendering a real Mako template.  For example, you might be creating HTML directly in Python but want the JS and CSS in regular .js/.jsm/.css/.cssm files.

Obviously, you should normally be using templates to generate HTML, but you might have a custom widgets that are created good old Python.  If these widgets have a significant amount of JS and/or CSS, you may want to keep them in regular files instead of big ol' strings in your code.

By calling DMP's "fake template" functions, you can leverage its automatic discovery of static files, including rendering and caching of script/style template files and compilation of .scss files.  DMP already knows how to cache and render, so why not let it do the work for you?

For example, suppose you are creating HTML in some code within a `myapp` view file.  Even though you aren't using a template file, you can still include JS and CSS automatically:

```python
from django_mako_plus import get_fake_template_css, get_fake_template_js

def myfunction(request):
    # generate the html
    html = []
    html.append('<div>All your html content belong to us</div>')
    html.append('<div>Some more html</div>')

    # set up a context to pass into the .cssm and .jsm
    context = { 'four': 2 + 2 }

    # include/render two css files if they exist): myapp/styles/mytemplate.css and myapp/styles/mytemplate.cssm
    html.append(get_fake_template_css(request, 'myapp', 'mytemplate.fakehtml', context))

    # include/render two js files if they exist): myapp/scripts/mytemplate.js and myapp/scripts/mytemplate.jsm
    html.append(get_fake_template_js(request, 'myapp', 'mytemplate.fakehtml', context))

    # return the joined content
    return '\n'.join(html)
```

And no, you really didn't need the `.fakehtml` extension on the template name.  Any extension (or no extension) will do.

# Where to Now?

This tutorial has been an introduction to the Django-Mako-Plus framework.  The primary purpose of DMP is to combine the excellent Django system with the also excellent Mako templating system.  And, as you've hopefully seen above, this framework offers many other benefits as well.  It's a new way to use the Django system.

I suggest you continue with the following:

* Go through the [Mako Templates](http://www.makotemplates.org/) documentation.  It will explain all the constructs you can use in your html templates.
* Read or reread the [Django Tutorial](http://www.djangoproject.com/). Just remember as you see the tutorial's Django template code (usually surrounded by `{{  }}`) that you'll be using Mako syntax instead (`${  }`).
* Link to this project in your blog or online comments.  I'd love to see the Django people come around to the idea that Python isn't evil inside templates.  Complex Python might be evil, but Python itself is just a tool within templates.
