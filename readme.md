# Use This If You've Said:

* Is there an alternative to Django templates?
* Why are Django templates weak sauce? Why not just use regular Python in templates?
* Why does Django make me list every. single. page. in urls.py?
* I'd like to include Python code in my CSS and Javascript files.
* My app's views.py file is getting HUGE.  How can I split it intelligently?
  
  
# Description

This app is a front controller that integrates the excellent Django framework with the also excellent Mako templating engine.  Django comes with its own template system, but it's fairly weak (by design).  Mako, on the other hand, is a fantastic template system that allows full Python code within HTML pages. 

> Author's Note: The primary reason Django doesn't allow full Python in its templates is the designers want to encourage you and I to keep template logic simple.  I fully agree with this philosophy.  I just don't agree with the "forced" part of this philosophy.  The Python way is rather to give freedom to the developer but train in the correct way of doing things.  Even though I fully like Python in my templates, I still keep them fairly simple.  Views are where your logic goes.

But wait, there's more! :)  Django-Mako-Plus adds the following features:

1. DMP uses the Mako templating engine rather than the weaker Django templating engine.  Why would I want to learn a whole new language for templating when Mako uses my favorite language: Python?

2. DMP allows calling views and html pages by convention rather than specific entries in urls.py. Any .html file on your site can be called without new entries in urls.py for every. single. new. page.  Doesn't Python favor convention over configuration?  

3. DMP introduces the idea of URL parameters.  These allow you to embed parameters in urls, Django style--meaning you can use pretty URLs like http://myserver.com/abc/def/123/ without specific entries in urls.py and without the need for traditional (i.e. ulgy) ?first=abc&second=def&third=123 syntax.

4. DMP separates view functions into different files rather than all-in-one style.  Anyone who has programmed Django long knows that the single views.py file in each app often gets looooonnng.  Splitting logic into separate files keeps things more orderly.

5. DMP automatically includes CSS and JS files, and it allows Python code within these files.  These static files get included in your web pages without any explicit declaration of `<link>` or `<script>` elements.  This means that `mypage.css` and `mypage.js` get linked in `mypage.html` automatically.  Python code within these support files means your CSS can change based on user or database entries.

But don't worry, you'll still get all the Django goodness with its fantastic ORM, views, forms, etc.

## Where Is DMP Used?

This app was developed at MyEducator.com, primarily by Dr. Conan C. Albrecht <ca@byu.edu>.  You can view my blog at http://goalbrecht.com/.  Please email me if you find errors with this tutorial or have suggestions/fixes for the DMP framework.  Since I also use the framework in my Django classes at BYU, many students have implemented the framework at their companies upon graduation.  At this point, the framework is quite mature and robust.

I've been told by some that DMP has a lot in common with Rails.  I've actually never used RoR, but good ideas are good wherever they are found, right? :)


## Why Mako instead of Jinja2, Cheetah, or [insert template language here]?

Python has several mature, excellent templating languages.  Both Mako and Jinja2 are fairly recent yet mature systems.  Both are screaming fast.  Cheetah is an older system but has quite a bit of traction.  It wasn't a clear choice of one over the rest.

The short answer is I liked Mako's approach the best.  It felt the most Pythonic to me.  Jinja2 may feel more like Django's built-in template system, but Mako won out because it looked more like Python--and the point of DMP is to include Python in templates. 


## Comparison with Django Syntax

If you have read through the Django Tutorial, you've seen examples for templating in Django.  While the rest of Django, such as models, settings, migrations, etc., is the same (with or without DMP), the way you do templates will obviously change with DMP.  The following examples should help you understand the different between standard Django and DMP template syntax.

Note in the examples how the DMP column normally uses standard Python syntax, with no extra language to learn:

- Output the value of the question variable:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap><pre><code>{{ question }}</code></pre></td>
    <td nowrap><pre><code>${ question }</code></pre></td>
  </tr>
</table>
- Output a user's full name (a method on User):
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap><pre><code>{{ user.get_full_name }}</code></pre></td>
    <td nowrap><pre><code>${ user.get_full_name() }</code></pre></td>
  </tr>
</table>
- Iterate through a relationship:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap><pre><code>&lt;ul&gt;
  {% for choice in question.choice_set.all %}
    &lt;li&gt;{{ choice.choice_text }}&lt;/li&gt;
  {% endfor %}
&lt;/ul&gt;</code></pre></td>
    <td nowrap><pre><code>&lt;ul&gt;
  %for choice in question.choice_set.all():
    &lt;li&gt;${ choice.choice_text }&lt;/li&gt;
  %endfor
&lt;/ul&gt;</code></pre></td>
  </tr>
</table>
- Set a variable:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap><pre><code>{% with name="Sam" %}</code></pre></td>
    <td nowrap><pre><code>&lt;% name = &quot;Sam&quot; %&gt;</code></pre></td>
  </tr>
</table>
- Format a date:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap><pre><code>{{ value|date:"D d M Y" }}</code></pre></td>
    <td nowrap><pre><code>${ value.strftime('%D %d %M %Y') }</code></pre></td>
  </tr>
</table>
- Join a list:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap><pre><code>{{ mylist | join:', ' }}</code></pre></td>
    <td nowrap><pre><code>${ ', '.join(mylist) }</code></pre></td>
  </tr>
</table>
- Use the /static prefix:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap><pre><code>{% load static %}
&lt;img src=&quot;{% get_static_prefix %}images/hi.jpg&quot;/&gt;</code></pre></td>
    <td nowrap><pre><code>&lt;img src=&quot;${ settings.STATIC_ROOT }images/hi.jpg&quot;/&gt;</code></pre></td>
  </tr>
</table>
- Call a Python method:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td>Requires a custom tag, unless a built-in tag provides the behavior.</td>
    <td nowrap>Any Python method can be called:
<pre><code>&lt;%! import random %&gt;
${ random.randint(1, 10) }</code></pre></td>
  </tr>
</table>
- Output a default if empty:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap><pre><code>{{ value | default:"nothing" }}</code></pre></td>
    <td nowrap>
      Use a boolean:
      <pre><code>${ value or "nothing" }</code></pre>
      or use a Python if statement:
      <pre><code>${ value if value != None else "nothing" }</code></pre>
    </td>
  </tr>
</table>
- Run arbitrary Python (keep it simple, Tex!):
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap><pre><code>Requires a custom tag</code></pre></td>
    <td nowrap><pre><code>&lt;%
  i = 1
  while i &lt; 10:
    context.write(&#x27;&lt;p&gt;Testing {0}&lt;/p&gt;&#x27;.format(i))
    i += 1
%&gt;</code></pre></td>
  </tr>
</table>
- Inherit another template:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap><pre><code>{% extends "base.html" %}</code></pre></td>
    <td nowrap><pre><code>&lt;%inherit file=&quot;base.htm&quot; /&gt;</code></pre></td>
  </tr>
</table>
- Override a block:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap><pre><code>{% block title %}My amazing blog{% endblock %}</code></pre></td>
    <td nowrap><pre><code>&lt;%block name="title"&gt;My amazing blog&lt;/%block&gt;</code></pre></td>
  </tr>
</table>
- Link to a CSS file:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td nowrap>Place in each template: <pre><code>&lt;link rel=&quot;stylesheet&quot; type=&quot;text/css&quot; href=&quot;...&quot;&gt;</code></pre></td>
    <td>Simply name the .css/.js file the same name as your .html template.  DMP will include the link automatically.</td>
  </tr>
</table>
- Perform per-request logic in CSS or JS files:
<table>
  <tr>
    <th>Django Templates</th>
    <th>DMP (Mako) Templates</th>
  </tr><tr>
    <td>Create an entry in ``urls.py``, create a view, and render a template for the CSS or JS.</td>
    <td>Simply name the .css file as name.cssm for each name.html template.  DMP will render the template and include it automatically.</td>
  </tr>
</table>



# Installation


### Python 3+ (also 2.7)

* Install Python and ensure you can run "python3" at the command prompt.  The framework is developed on Python 3.x, but we've ensured it also works with 2.7 for those without a choice.
* Install PIP for `pip3` (it comes with Python 3.4+)

All of the above can be found on numerous Python tutorials and web sites.  They are standard methods of installing modules in Python.


### Install Django, Mako, and DMP

Simply use PIP, which comes with Python 3.4+.  If you are on an older Python version, you can install it from https://pip.pypa.io/en/latest/installing.html.
  
    pip3 install django
    pip3 install mako
    pip3 install django-mako-plus
   
   
### Create a Django project

Create a Django project with the typical:

    python3 django-admin.py startproject test_dmp
  
This step is described in detail in the standard Django tutorial.  You can, of course, name your project anything you want, but in the sections below, I'll assume you called your project `test_dmp`.

> If the django-admin.py command isn't found, it's probably not in your path.   This is a common problem to people new to Django, and the main Django has an entire page dedicated the problem.  Check it out at [https://docs.djangoproject.com/en/dev/faq/troubleshooting](https://docs.djangoproject.com/en/dev/faq/troubleshooting).
  
### Edit Your `settings.py` File:

1. Add `django_mako_plus.controller` to the end of your `INSTALLED_APPS` list:
   
    INSTALLED_APPS = (
        ...
        'django_mako_plus.controller',
    )
    
2. Add `django_mako_plus.controller.router.RequestInitMiddleware` to the end of your `MIDDLEWARE CLASSES` list:
   
    MIDDLEWARE_CLASSES = (
        ...
        'django_mako_plus.controller.router.RequestInitMiddleware',
    )       
    
3. Add a logger to help you debug (optional but highly recommended!):
   
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
    
4. Add the Django-Mako-Plus settings (paste this code at the end of your `settings.py` file):   
   
    ###############################################################
    ###   Specific settings for the Django-Mako-Plus app

    # identifies where the Mako template cache will be stored, relative to each app
    DMP_TEMPLATES_CACHE_DIR = 'cached_templates'

    # the default app and page to render in Mako when the url is too short
    DMP_DEFAULT_PAGE = 'index'  
    DMP_DEFAULT_APP = 'homepage'

    # these are included in every template by default - if you put your most-used libraries here, you won't have to import them exlicitly in templates
    DMP_DEFAULT_TEMPLATE_IMPORTS = [
      'import os, os.path, re',
    ]
    
    # whether to send the custom DMP signals -- set to False for a slight speed-up in router processing
    # determines whether DMP will send its custom signals during the process
    DMP_SIGNALS = True
    
    # whether to minify using rjsmin, rcssmin during 1) collection of static files, and 2) on the fly as .jsm and .cssm files are rendered
    # rjsmin and rcssmin are fast enough that doing it on the fly can be done without slowing requests down
    DMP_MINIFY_JS_CSS = True

    # see the DMP online tutorial for information about this setting
    DMP_TEMPLATES_DIRS = [ 
      # os.path.join(BASE_DIR, 'base_app', 'templates'),
    ]

    ###  End of settings for the base_app Controller
    ################################################################
    
5. Add the following to serve your static files.  This step is pure Django; you can read about it in the standard Django docs.  These variables are also explained below in the section entitled "Static Files, Your Web Server, and DMP".

    STATIC_URL = '/static/'
    STATICFILES_DIRS = (
        # SECURITY WARNING: this next line must be commented out at deployment
        BASE_DIR,  
    )
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')  

    
### Enable the Django-Mako-Plus Router

Add the Django-Mako-Plus router as **the last pattern** in your `urls.py` file:

     urlpatterns = patterns('',
     
         ...

         # the django_mako_plus controller handles every request - this line is the glue that connects Mako to Django
         url(r'^.*$', 'django_mako_plus.controller.router.route_request' ),
     ) 
     
### Create a DMP-Style App

Change to your project directory in the terminal/console, then create a new Django-Mako-Plus app with the following:

        python3 manage.py dmp_startapp homepage
        
As with any Django app, you need to add your new app to the INSTALLED_APPS list in `settings.py`:

        INSTALLED_APPS = (
       ...
       'homepage',
        )
        
Congratulations.  You're ready to go!

### Huh? "app homepage is not a designated DMP app"?

If DMP tells you that an app you're trying to access "is not a designated DMP app", you missed something above.  Rather than go above and trying again, go on to the next section on converting existing apps for a summary of everything needed to make a valid DMP app.  You're likely missing something in this list, and by going through this next section, you'll ensure all the needed pieces are in place.  I'll bet you don't the `DJANGO_MAKO_PLUS = True` part in your app's init file.  Another possible reason is you didn't list `homepage` as one of your `INSTALLED_APPS` as described above.


### Convert Existing Apps to DMP

Already have an app that you'd like to switch over?  Just do the following:

* Ensure your app is listed in your `settings.py` file's `INSTALLED_APPS` list.

* Create folders within your app so you match the following structure:

        your-app/
       __init__.py
       media/
       scripts/
       styles/
       templates/
       views/
           __init__.py
        
* Add the following to `your-app/__init__.py`.  This signals that your app is meant to be used with DMP.  If you don't have this variable, DMP will complain that your app isn't a 'DMP app'.

        DJANGO_MAKO_PLUS = True
    
* Go through your existing `your-app/views.py` file and move the functions to new files in the `your-app/views/` folder.  You need a .py file for *each* web-accessible function in your existing views.py file.  For example, if you have an existing views.py function called `do_something` that you want accessible via the url `/your-app/do_something/`, create a new file `your-app/views/do_something.py`.  Inside this new file, create the function `def process_request(request):`, and copy the contents of the existing function within this function.  Decorate each process_request with the `@view_function` decorator.

* Clean up: once your functions are in new files, you can remove the `your-app/views.py` file.  You can also remove all the entries for your app in `urls.py`.
      

# Tutorial

I'll assume you've just installed Django-Mako-Plus according to the instructions above.  You should have a `dmp_test` project directory that contains a `homepage` app.  I'll further assume you know how to open a terminal/console and `cd` to the `dmp_test` directory.  Most of the commands below are typed into the terminal in this directory.

**Quick Start:** You already have a default page in the new app, so fire up your server with `python3 manage.py runserver` and go to [http://localhost:8000/homepage/index/](http://localhost:8000/homepage/index/).  

You should see a congratulations page.  If you don't, go back to the installation section and walk through the steps again.  Your console might have valuable error messages to help troubleshoot things. 

### The DMP Structure

Let's explore the directory structure of your new app:

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

The directories should be fairly self-explanatory. Note they are **different** than a traditional Django app structure.  Put images and other support files in media/, Javascript in scripts/, CSS in styles/, html files in templates/, and Django views in views/.

The following setting is automatically done when you run `dmp_startapp`, but if you created your app structure manually, DMP-enabled apps must have the following in the `appname/__init__.py` file:

        DJANGO_MAKO_PLUS = True

Let's start with the two primary html template files: `base.htm` and `index.html`.  

`index.html` is pretty simple:

        <%inherit file="base.htm" />

        <%block name="content">
       <div class="content">
         <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
         <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
       </div>
        </%block>

If you are familiar with Django templates, you'll recognize the template inheritance in the `<%inherit/>` tag.  However, this is Mako code, not Django code, so the syntax is a little different.  The file defines a single block, called `content`, that is plugged into the block by the same name in the code below.

The real HTML is kept in the `base.htm` file.  It looks like this:

        ## this is the skeleton of all pages on in this app - it defines the basic html tags

        ## set up a StaticRenderer object to enable the CSS/JS automatic inclusion magic.
        <%! from django_mako_plus.controller import static_files %>
        <%  static_renderer = static_files.StaticRenderer(self) %>

        <!DOCTYPE html>
        <html>
     <meta charset="UTF-8">
     <head>
    
       <title>homepage</title>
    
       ## add any site-wide scripts or CSS here; for example, jquery:
       <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
  
       ## render the css with the same name as this page
       ${ static_renderer.get_template_css(request, context)  }
  
     </head>
     <body>
  
       <header>
         Welcome to the homepage app!
       </header>
  
       <%block name="content">
         Site content goes here in sub-templates.
       </%block>  
  
       ## render the JS with the same name as this page
       ${ static_renderer.get_template_js(request, context)  }
  
     </body>
        </html>

Pay special attention to the `<%block name="content">` section, which is overridden in `index.html`.  The page given to the browser will look exactly like `base.htm`, but the `content` block will come from `index.html` rather than the one defined in the supertemplate.

The purpose of the inheritance from `base.htm` is to get a consistent look, menu, etc. across all pages of your site.  When you create additional pages, simply override the `content` block, similar to the way `index.html` does it.



## Routing Without urls.py

In the installation procedures above, you added the following line to your urls.py routing file:

        url(r'^.*$', 'django_mako_plus.controller.router.route_request' ),

The regular expression in this line, `^.*$`, is a wildcard that matches everything.  It tells every url to go to the Django-Mako-Plus router, where it is further routed according to the pattern: `/app/page`.  We aren't really routing without `urls.py`; we're adding a second, more important router afterward.  In fact, you can still use the `urls.py` file in the normal Django way because we placed the wildcard at the *end* of the file.  Things like the `/admin/` still work the normal, Django way.

Rather than listing every. single. page. on. your. site. in the `urls.py` file, the router figures out the destination via a convention.  The first url part is taken as the app to go to, and the second url part is taken as the view to call.

For example, the url `/homepage/index/` routes as follows:

* The first url part `homepage` specifies the app that will be used.
* The second url part `index` specifies the view or html page within the app.  In our example:
  * The router first looks for `homepage/views/index.py`.  In this case, it fails because we haven't created it yet.
  * It then looks for `homepage/templates/index.html`.  It finds the file, so it renders the html through the Mako templating engine and returns it to the browser.
  
The above illustrates the easiest way to show pages: simply place .html files in your templates/ directory.  This is useful for pages that don't have any "work" to do.  Examples might be the "About Us" and "Terms of Service" pages.  There's usually no functionality or permissions issues with these pages, so no view function is required.

> What about the case where a page isn't specified, such as `/homepage/`?  If the url doesn't contain two parts, the router goes to the default page as specified in your settings.py `DMP_DEFAULT_PAGE` variable.  This allows you to have a "default page", similar to the way web servers default to the index.html page.  If the path is entirely empty (i.e. http://www.yourserver.com/ with *no* path parts), the router uses both defaults specified in your settings.py file: `DMP_DEFAULT_PAGE` and `DMP_DEFAULT_APP`.

## Adding a View Function

Let's add some "work" to the process by adding the current server time to the index page.  Create a new file `homepage/views/index.py` and copy this code into it:

        from django.conf import settings
        from django_mako_plus.controller import view_function
        from django_mako_plus.controller.router import get_renderer
        from datetime import datetime

        templater = get_renderer('homepage')

        @view_function
        def process_request(request):
     template_vars = {
       'now': datetime.now(),
     }
     return templater.render_to_response(request, 'index.html', template_vars)
  
Reload your server and browser page, and you should see the exact same page.  It might look the same, but something very important happened in the routing.  Rather than going straight to the `index.html` page, processing went to your new `index.py` file.  At the end of the `process_request` function above, we manually render the `index.html` file.  In other words, we're now doing extra "work" before the rendering.  This is the place to do database connections, modify objects, prepare and handle forms, etc.  It keeps complex code out of your html pages.

Let me pause for a minute and talk about log messages.  If you enabled the logger in the installation, you should see the following in your console:

     DEBUG controller :: processing: app=homepage, page=index, funcname=, urlparams=['']
     DEBUG controller :: calling view function homepage.views.index.process_request
     DEBUG controller :: rendering template .../dmptest/homepage/templates/index.html  

These debug statements are incredibly helpful in figuring out why pages aren't routing right.  If your page didn't load right, you'll probably see why in these statements.  In my log above, the first line lists what the controller assigned the app and page to be.

The second line tells me the controller found my new `index.py` view, and it called the `process_request` function successfully.  This is important -- the `process_request` function is the "default" view function.  Further, the any web-accessible function must be decorated with `@view_function`.

>This decoration with `@view_function` is done for security.  If the framework let browsers specify any old function, end users could invoke any function of any module on your system!  By requiring the decorator, the framework limits end users to one specifically-named function.

> Later in the tutorial, we'll describe another way to call other functions within your view  Even though `process_request` is the default function, you can actually have multiple web-accessible functions within a view/*.py file.

As stated earlier, we explicitly call the Mako renderer at the end of the `process_request` function.  The template_vars (the third parameter of the call) is a dictionary containing variable names that will be globally available within the template.

Let's use the `now` variable in our index.html template:

        <%inherit file="base.htm" />

        <%block name="content">
       <div class="content">
         <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
         <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
         <p class="server-time">The current server time is ${ now }.</p>
         <p class="browser-time">The current browser time is...</p>
       </div>
        </%block>

The `${ varname }` code is Mako syntax and is described more fully on the Mako web site.  Right now, it's most important that you see how to send data from the view to the template.  If you already know Django templates, it's pretty close to the same pattern.  The Django-Mako-Framework tries to improve Django, not entirely change it.

Reload your web page and ensure the new view is working correctly.  You should see the server time printed on the screen.  Each time you reload the page, the time should change.

> You might be wondering about the incomplete sentence under the .browser_time paragraph.  Just hold tight.  We'll be using this later in the tutorial.


## URL Parameters

Django is all about pretty urls.  In keeping with that philosophy, this framework has URL parameters.  We've already used the first two items in the path: the first specifies the app, the second specifies the view/template.  URL parameters are the third part, fourth part, and so on.

In traditional web links, you'd specify parameters using key=value pairs, as in `/homepage/index?first=abc&second=def`.  That's ugly, of course, and it's certainly not the Django way (it does still work, though).

With DMP, you have another, better option available.  You'll specify parameters as `/homepage/index/abc/def/`.  The controller makes them available to your view as `request.urlparams[0]` and `request.urlparams[1]`.  

Suppose you have a product detail page that needs the SKU number of the product to display.  A nice way to call that page might be `/catalog/product/142233342/`.  The app=catalog, view=product.py, and urlparams[0]=142233342.

These prettier links are much friendlier when users bookmark them, include them in emails, and write them down.  It's all part of coding a user-friendly web site.

Note that URL parameters don't take the place of form parameters.  You'll still use GET and POST parameters to submit forms.  URL parameters are best used for object ids and other simple items that pages need to display. 

Although this might not be the best use of urlparams, suppose we want to display our server time with user-specified format.  On a different page of our site, we might present several different `<a href>` links to the user that contain different formats (we wouldn't expect users to come up with these urls on their own -- we'd create links for the user to click on).  Change your `index.py` file to use a url-specified format for the date:
  
        from django.conf import settings
        from django_mako_plus.controller import view_function
        from django_mako_plus.controller.router import get_renderer
        from datetime import datetime

        templater = get_renderer('homepage')

        @view_function
        def process_request(request):
     template_vars = {
       'now': datetime.now().strftime(request.urlparams[0] if request.urlparams[0] else '%H:%M'),
     }
     return templater.render_to_response(request, 'index.html', template_vars)

The following links now give the time in different formats:

* The default format: `http://localhost:8000/homepage/index/`
* The current hour: `http://localhost:8000/homepage/index/%H/`
* The month, year: `http://localhost:8000/homepage/index/%B,%20%Y`

> If a urlparam doesn't exist, it always returns the empty string ''.  This is slightly different than a regular Python list, which throws an exception when an index is too large.  This means that request.urlparams[50] returns the empty string rather than an exception.  The `if` statement in the code above can be used to determine if a urlparam exists or not.  Another way to code a default value for a urlparam is `request.urlparam[2] or 'some default value'`.  


## A Bit of Style

Modern web pages are made up of three primary parts: html, CSS, and Javascript (images and other media might be a fourth, but we'll go with three for this discussion).  Since all of your pages need these three components, this framework combines them intelligently for you.  All you have to do is name the .html, the css., and the .js file with the same name, and DMP will automatically generate the `<link>` and `<script>` tags for you.  It will even put them in the "right" spot in the html (styles at the beginning, scripts at the end).

To style our index.html file, create `homepage/styles/index.css` and copy the following into it:

        .server-time {
     font-size: 2em;
     color: red;
        }

When you refresh your page, the server time should be styled with large, red text.  If you view the html source in your browser, you'll see a new `<link...>` near the top of your file.  It's as easy as naming the files the same and placing the .css file in the styles/ directory.

> You might be wondering about the big number after the html source `<link>`.  That's the server start time, in minutes since 1970.  This is included because browsers (especially Chrome) don't automatically download new CSS files.  They use their cached versions until a specified date, often far in the future. By adding a number to the end of the file, browsers will think the CSS files are "new" whenever you restart your server.  Whenever you need to send CSS changes to clients and have them ignore their caches, simply restart your server!  Trixy browserses...

The framework knows how to follow template inheritance.  For example, since `index.html` extends from `base.htm`, we can actually put our CSS in any of **four** different files: `index.css`, `index.cssm`, `base.css`, and `base.cssm` (the .cssm files are explained in the next section).  Place your CSS styles in the appropriate file, depending on where the HTML elements are located.  For example, let's style our header a little.  Since the `<header>` element is in `base.htm`, create `homepage/styles/base.css` and place the following in it:
  
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

Reload your browser, and you should have a nice white on blue header. If you view source in the browser, you'll see the CSS files were included as follows:

        <link rel="stylesheet" type="text/css" href="/static/homepage/styles/base.css?33192040" />
        <link rel="stylesheet" type="text/css" href="/static/homepage/styles/index.css?33192040" />

Note that `base.css` is included first because it's at the top of the hierarchy.  Styles from `index.css` override any conflicting styles from `base.css`, which makes sense because `index.html` is the final template in the inheritance chain.


## A Bit of Style, Reloaded

The style of a web page is often dependent upon the user, such as a user-definable theme in an online email app or a user-settable font family in an online reader.  DMP supports this behavior, mostly because the authors at MyEducator needed it for their online book reader.  You can use Mako (hence, any Python code) not only in your .html files, but also in your CSS and JS files.  Simply name the file with `.cssm` rather than .css.  When the framework sees `index.cssm`, it runs the file through the Mako templating engine before it sends it out.

> Since we assume .cssm files are generated per user, they are embedded directly in the HTML rather than linked.  This circumvents a second call to the server, which would happen every time since the CSS is being dynamically generated.  Dynamic CSS can't be cached by a browser any more than dynamic HTML can.

Let's make the color dynamic by adding a new random variable `timecolor` to our index.py view:

        from django.conf import settings
        from django_mako_plus.controller import view_function
        from django_mako_plus.controller.router import get_renderer
        from datetime import datetime
        import random

        templater = get_renderer('homepage')

        @view_function
        def process_request(request):
     template_vars = {
       'now': datetime.now().strftime(request.urlparams[0] if request.urlparams[0] else '%H:%M'),
       'timecolor': random.choice([ 'red', 'blue', 'green', 'brown' ]),
     }
     return templater.render_to_response(request, 'index.html', template_vars)

Now, rename your index.css file to `index.cssm`.  Then set the content of index.cssm to the following:

        .server-time {
     font-size: 2em;
     color: ${ timecolor };
        }
  
Refresh your browser a few times.  The color should change with each refresh! 

As shown in the example above, the template_vars dictionary sent the templating engine in `process_request` are globally available in .html, .cssm, and .jsm files.

> Note that this behavior is different than CSS engines like Less and Sass. Most developers use Less and Sass for variables at development time.  These variables are rendered and stripped out before upload to the server, and they become static, normal CSS files on the server.  .cssm files should be used for dynamically-generated, per-request CSS.


## Static and Dynamic Javascript

Javascript files work the same way as CSS files, so if you skipped the two CSS sections above, you might want to go read through them.  This section will be more brief because it's the same pattern again.  Javascript files are placed in the `scripts/` directory, and both static `.js` files and dynamically-created `.jsm` files are supported. 

Let's add a client-side, Javascript-based timer.  Create the file `homepage/scripts/index.js` and place the following JQuery code into it:

        $(function() {
     // update the time every 1 seconds
     window.setInterval(function() {
       $('.browser-time').text('The current browser time is ' + new Date() + '.');
     }, 1000);
        });

Refresh your browser page, and you should see the browser time updating each second.  Congratulations, you've now got a modern, HTML5 web page. :)

Let's also do an example of a `.jsm` (dynamic) script.  We'll let the user set the browser time update period through a urlparam.  We'll leave the first parameter alone (the server date format) and use the second parameter to specify this interval. 

First, **be sure to change the name of the file from `index.js` to `index.jsm`.**  This tells the framework to run the code through the Mako engine before sending to the browser.  In fact, if you try leaving the .js extension on the file and view the browser source, you'll see the `${ }` Mako code doesn't get rendered.  It just gets included like static html.  Changing the extension to .jsm causes DMP to run Mako and render the code sections.

Update your `homepage/scripts/index.jsm` file to the following:

        $(function() {
     // update the time every 1 seconds
     window.setInterval(function() {
       $('.browser-time').text('The current browser time is ' + new Date() + '.');
     }, ${ request.urlparams[1] });
        });

Save the changes and take your browser to [http://localhost:8000/homepage/index/%Y/3000/](http://localhost:8000/homepage/index/%Y/3000/).  Since urlparams[1] is 3000 in this link, you should see the date change every three seconds.  Feel free to try different intervals, but out of concern for the innocent (e.g. your browser), I'd suggest keeping the interval above 200 ms.

> I should note that letting the user set date formats and timer intervals via the browser url are probably not the most wise or secure ideas.  But hopefully, it is illustrative of the different abilities of the Django-Mako-Plus framework.


## Behind the Curtain

After reading the previous sections on automatic CSS and JS inclusion, you might want to know how it works.  It's all done in the templates (base.htm now, and base_ajax.htm in a later section below) you are inheriting from.  Open `base.htm` and look at the following code:

        ## set up a StaticRenderer object to enable the CSS/JS automatic inclusion magic.
        <%! from django_mako_plus.controller import static_files %>
        <%  static_renderer = static_files.StaticRenderer(self) %>

        ...

        ## render the css with the same name as this page
        ${ static_renderer.get_template_css(request, context)  }

        ...

        ## render the JS with the same name as this page
        ${ static_renderer.get_template_js(request, context)  }

The first block at the top of the file sets up a `static_renderer` object, which comes with this framework.  This object checks for the various .css, .cssm, .js, and .jsm files as the template is being rendered.  The next two calls, `get_template_css()` and `get_template_js()` include the `<link>`, `<script>`, and other code based on what it finds.
  
This all works because the `index.html` template extends from the `base.htm` template.  If you fail to inherit from `base.htm` or `base_ajax.htm`, the `static_renderer` won't be able to include the support files.




## Ajax Calls

What would the modern web be without Ajax?  Well, truthfully, a lot simpler. :)  In fact, if we reinvented the web with today's requirements, we'd probably end up at a very different place than our current web. Even the name ajax implies the use of xml -- which we don't use much in ajax anymore. Most ajax calls return json or html these days!

But regardless of web history, ajax is required on most pages today.  I'll assume you understand the basics of ajax and focus specifically on the ways this framework supports it.

Suppose we want to reload the server time every few seconds, but we don't want to reload the entire page.  Let's start with the client side of things.  Let's place a refresh button in `homepage/templates/index.html`:

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

Note the new `<button>` element in the above html.  Next, we'll add Javascript to the `homepage/scripts/index.jsm` file that runs when the button is clicked:

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

The client side is now ready, so let's create the `/homepage/index_time/` server endpoint.  Create a new `homepage/views/index_time.py` file:

        from django.conf import settings
        from django_mako_plus.controller import view_function
        from django_mako_plus.controller.router import get_renderer
        from datetime import datetime
        import random

        templater = get_renderer('homepage')

        @view_function
        def process_request(request):
     template_vars = {
       'now': datetime.now(),
     }
     return templater.render_to_response(request, 'index_time.html', template_vars)
  
Finally, create the `/homepage/templates/index_time.html` template, which is rendered at the end of `process_request()` above:

        <%inherit file="base_ajax.htm" />

        <%block name="content">
     The current server time is ${ now }.
        </%block>

Note that this template inherits from `base_ajax.htm`.  If you open `base_ajax.htm`, you'll see it doesn't have the normal `<html>`, `<body>`, etc. tags in it.  This supertemplate is meant for snippets of html rather than entire pages.  What it **does** contain is the calls to the `static_renderer` -- the real reason we inherit rather than just have a standalone template snippet.  By calling `static_renderer` in the supertemplate, any CSS or JS files are automatically included with our template snippet.  Styling the ajax response is as easy as creating a `homepage/styles/index_time.css` file.

> We really didn't need to create `index_time.html` at all. Just like in Django, a process_request view can simply return an `HttpResponse` object.  At the end of process_request, we simply needed to `return HttpResponse('The current server time is %s' % now)`.  The reason I'm rendering a template here is to show the use of `base_ajax.htm`, which automatically includes .css and .js files with the same name as the template.

Reload your browser page and try the button.  It should reload the time *from the server* every time you push the button.


## Really, a Whole New File for Ajax?

All right, there **is** a shortcut, and a good one at that. The last section showed you how to create an ajax endpoint view.  Since modern web pages have many little ajax calls thoughout their pages, the framework allows you to put several web-accessible methods **in the same .py file**.  

Let's get rid of `homepage/views/index_time.py`.  That's right, just delete the file.

Open `homepage/views/index.py` and add the following to the end of the file:

        @view_function
        def gettime(request):
     template_vars = {
       'now': datetime.now(),
     }
     return templater.render_to_response(request, 'index_time.html', template_vars)  

Note the function is decorated with `@view_function`, and it contains the function body from our now-deleted `index_time.py`.  The framework recognizes **any** function with this decorator as an available endpoint for urls, not just the hard-coded `process_request` function.  In other words, you can actually name your view methods any way you like, as long as you follow the pattern described in this section.  

In this case, getting the server time is essentially "part" of the index page, so it makes sense to put the ajax endpoint right in the same file.  Both `process_request` and `gettime` serve content for the `/homepage/index/` html page.  Having two view files is actually more confusing to a reader of your code because they are so related.   Placing two view functions (that are highly related like these are) in the same file keeps everything together and makes your code more concise and easier to understand.

To take advantage of this new function, let's modify the url in `homepage/scripts/index.jsm`:

        // update button
        $('#server-time-button').click(function() {
     $('.server-time').load('/homepage/index.gettime');
        });

The url now points to `index.gettime`, which the framework translates to `index.py -> gettime()`.  In other words, a dot (.) gives an exact function within the module to be called rather than the default `process_request` function.

Reload your browser page, and the button should still work.  Press it a few times and check out the magic.

In other words, a full DMP url is really `/app/view.function/`.  Using `/app/view/` is a shortcut, and the framework translates it as `/app/view.process_request/` internally.

> Since ajax calls often return JSON, XML, or simple text, you often only need to add a function to your view.  At the end of the function, simply `return HttpResponse("json or xml or text")`.  You likely don't need full template, css, or js files.


## Templates Located Elsewhere

This likely impacts few users of DMP, so you may want to skip this section for now.  Suppose your templates are located in a directory outside your normal project root.  In other words, for some reason, you don't want to put your templates in the app/templates directory.  


### Case 1: Templates Within Your Project Directory

If the templates you need to access are within your project directory, no extra setup is required.  Simply reference those templates relateive to the root project directory.  For example, to access a template located at homepage/mytemplates/sub1/page.html (relative to your project root), use the following:

        return templater.render_to_response(request, '/homepage/mytemplates/sub1/page.html', template_vars)
        
### Case 2: Templates Outside Your Project Directory

Suppose your templates are located on a different disk or entirely different directory, relative to your project.  DMP allows you to add extra directories to the template search path through the `DMP_TEMPLATES_DIRS` setting.  This variable contains a list of directories that are searched by DMP regardless of the app being referenced.  To include the `/var/templates/` directory in the search path, set this variable as follows:

        DMP_TEMPLATES_DIRS = [ 
      '/var/templates/',
        ]

Suppose, after making the above change, you need to render the '/var/templates/page1.html' template:

        return templater.render_to_response(request, 'page1.html', template_vars)
        
DMP will first search the current app's `templates` directory (i.e. the normal way), then it will search the `DMP_TEMPLATES_DIRS` list, which in this case contains `/var/templates/`.  Your `page1.html` template will be found and rendered.


## Template Inheritance Across Apps

You may have noticed that this tutorial has focused on a single app.  Most projects consist of many apps.  For example, a sales site might have an app for user management, an app for product management, and an app for the catalog and sales/shopping-cart experience.  All of these apps probably want the same look and feel, and all of them likely want to extend from the **same** `base.htm` file.

When you run `python3 manage.py dmp_startapp <appname>`, you get **new** `base.htm` and `base_ajax.htm` files each time.  This is done to get you started on your first app.  On your second, third, and subsequent apps, you probably want to delete these starter files and instead extend your templates from the `base.htm` and `base_ajax.htm` files in your first app.
  
In fact, in my projects, I usually create an app called `base_app` that contains the common `base.htm` html code, site-wide CSS, and site-wide Javascript.  Subsequent apps simply extend from `/base_app/templates/base.htm`.  The common `base_app` doesn't really have end-user templates in it -- they are just supertemplates that support other, public apps.

DMP supports cross-app inheritance by including your project root (e.g. `settings.BASE_DIR`) in the template lookup path.  All you need to do is use the full path (relative to the project root) to the template in the inherits statement.

Suppose I have the following app structure:

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

I want `homepage/templates/index.html` to extend from `base_app/templates/site_base.htm`.  The following code in `index.html` sets up the inheritance:

        <%inherit file="/base_app/templates/site_base.htm" />

> In fact, my pages are often three inheritance levels deep: `base_app/templates/site_base.htm -> homepage/templates/base.htm -> homepage/templates/index.html` to provide for site-wide page code, app-wide page code, and specific page code.




## Importing Python Modules into Templates

It's easy to import Python modules into your Mako templates.  Simply use a module-level block:

        <%!
     import datetime
     from decimal import Decimal
        %>

or a Python-level block (see the Mako docs for the difference):

        <%
     import datetime
     from decimal import Decimal
        %>

There may be some modules, such as `re` or `decimal` that are so useful you want them available in every template of your site.  In settings.py, simply add these to the `DMP_DEFAULT_TEMPLATES_IMPORTS` variable:

        DMP_DEFAULT_TEMPLATE_IMPORTS = [
     'import os, os.path, re',
     'from decimal import Decimal',
        ]

Any entries in this list will be automatically included in templates throughout all apps of your site.  With the above imports, you'll be able to use `re` and `Decimal` and `os` and `os.path` anywhere in any .html, .cssm, and .jsm file.


## Mime Types and Status Codes

The `render_to_response()` function returns the *text/html* mime type and *200* status code.  What if you need to return JSON, CSV, or a 404 not found?  Just wrap the `render` function in a standard Django `HttpResponse` object.  A few examples:

        from django.http import HttpResponse
        
        # return CSV
        return HttpResponse(templater.render(request, 'my_csv.html', {}), mimetype='text/csv')
        
        # return a custom error page
        return HttpResponse(templater.render(request, 'custom_error_page.html', {}), status=404)
        

## Useful Variables

At the beginning of each request (as part of its middleware), DMP adds a number of fields to the request object.  These 
variables primarily support the inner workings of the DMP router, but they may be useful to you as well.  The following
are available throughout the request:

* `request.dmp_router_app`: The Django application specified in the URL.  In the URL `http://www.server.com/calculator/index/1/2/3`, the `dmp_router_app` is the string "calculator".
* `request.dmp_router_page`: The name of the Python module specified in the URL.  In the URL `http://www.server.com/calculator/index/1/2/3`, the `dmp_router_page` is the string "index".  In the URL `http://www.server.com/calculator/index.somefunc/1/2/3`, the `dmp_router_page` is still the string "index".
* `request.dmp_router_page_full`: The exact module name specified in the URL, including the function name if specified.  In the URL `http://www.server.com/calculator/index/1/2/3`, the `dmp_router_page_full` is the string "index".  In the URL `http://www.server.com/calculator/index.somefunc/1/2/3`, the `dmp_router_page` is the string "index.somefunc".  Note the difference in this last example to what `dmp_router_page` reports.
* `request.dmp_router_function`: The name of the function within the module that will be called, even if it is not specified in the URL.  In the URL `http://www.server.com/calculator/index/1/2/3`, the `dmp_router_function` is the string "process_request" (the default function).  In the URL `http://www.server.com/calculator/index.somefunc/1/2/3`, the `dmp_router_page` is the string "somefunc".  
* `request.dmp_router_module`: The name of the real Python module specified in the URL, as it will be imported into the runtime module space.  In the URL `http://www.server.com/calculator/index/1/2/3`, the `dmp_router_module` is the string "calculator.views.index". 
* `request.urlparams`: A list of parameters specified in the URL.  See the section entitled "URL Parameters" above for more information.


## Static Files, Your Web Server, and DMP

Static files are files linked into your html documents like `.css` and `.js` as well as images files like `.png` and `.jpg`.  These are served directly by your web server (Apache, Nginx, etc.) rather than by Django because they don't require any processing.  They are just copied across the Internet.  Serving static files is what web servers were written for, and they are better at it than anything else.

Django-Mako-Plus works with static files the same way that traditional Django does, with one difference: the folder structure is different in DMP.  The folllowing subsections describe how you should use static files with DMP.

> If you read nothing else in this tutorial, be sure to read through the Deployment subsection given shortly.  There's a potential security issue with static files that you need to address before deploying.  Specifically, you need to comment out `BASE_DIR` from the setup shown next.


### Static File Setup

In your project's settings.py file, be sure you the following:

        STATIC_URL = '/static/'
        STATICFILES_DIRS = (
       BASE_DIR,  
        )
        STATIC_ROOT = os.path.join(BASE_DIR, 'static')  

### Development

During development, Django will use the `STATICFILES_DIRS` variable to find the files relative to your project root.  You really don't need to do anything special except ensure that the `django.contrib.staticfiles` app is in your list of `INSTALLED_APPS`.  Django's `staticfiles` app is the engine that statics files during development.

Simply place media files for the homepage app in the homepage/media/ folder.  This includes images, videos, PDF files, etc. -- any static files that aren't Javascript or CSS files.

Reference static files using the `${ STATIC_FILES }` variable.  For example, reference images in your html pages like this: 

        <img src="${ STATIC_URL }homepage/media/image.png" />

By using the `STATIC_URL` variable from settings in your urls rather than hard-coding the `/static/` directory location, you can change the url to your static files easily in the future.



### Security at Deployment (VERY Important)

At production/deployment, comment out `BASE_DIR` because it essentially makes your entire project available via your static url (a serious security concern):

        STATIC_URL = '/static/'
        STATICFILES_DIRS = (
        #    BASE_DIR,  
        )
        STATIC_ROOT = os.path.join(BASE_DIR, 'static')  

When you deploy to a web server, run `dmp_collectstatic` to collect your static files into a separate directory (called `/static/` in the settings above).  You should then point your web server (Apache, Nginx, IIS, etc.) to serve this folder directly to browsers.  For example, in Nginx, you'd set the following:

        location /static/ {
     alias /path/to/your/project/static/;
     access_log off;
     expires 30d;
        }

In Apache, you'd set the following:

Alias /static/ /path/to/your/project/static/

        <Directory /path/to/your/project/static/>
        Order deny,allow
        Allow from all
        </Directory>

        ### Collecting 


### Collecting Static Files

DMP comes with a manage.py command `dmp_collectstatic` that copies all your static resource files into a single subtree so you can easily place them on your web server.  At development, your static files reside within the apps they support.  For example, the `homepage/media` directory is a sibling to `homepage/views` and `/homepage/templates`.  This combined layout makes for nice development, but a split layout is more optimal for deployment because you have two web servers active at deployment (a traditional server like Apache doing the static files and a Python server doing the dynamic files).

The Django-Mako-Plus framework has a different layout than traditional Django, so it comes with its own static collection command.  When you are ready to publish your web site, run the following to split out the static files into a single subtree:

        python3 manage.py dmp_collectstatic
        
This command will copy of the static directories--`/media/`, `/scripts/`, and `/styles/`--to a common subtree called `/static/` (or whatever `STATIC_ROOT` is set to in your settings).  Everything in these directories is copied (except dynamic `*.jsm/*.cssm` files, which aren't static).

> Since this new `/static/` directory tree doesn't contain any of your templates, views, settings, or other files, you can make the entire subtree available via your web server.  This gives you the best combination of speed and security and is the whole point of this exercise.

The `dmp_collectstatic` command has the following command-line options:

* The commmand will refuse to overwrite an existing `/static/` directory.  If you already have this directory (either from an earlier run or for another purpose), you can 1) delete it before collecting static files, or 2) specify the overwrite option as follows:

        python3 manage.py dmp_collectstatic --overwrite

* If you need to ignore certain directories or filenames, specify them with the `--ignore` option.  This can be specified more than once, and it accepts Unix-style wildcards:

        python3 manage.py dmp_collectstatic --ignore=cached_templates --ignore=fixtures --ignore=*.txt



### Minification of JS and CSS

DMP will try to minify your *.js and *.css files using the `rjsmin` and `rcssmin` modules if the settings.py `DMP_MINIFY_JS_CSS` is True.  Your Python installation must also have these modules installed 

These two modules do fairly simplistic minification using regular expressions.  They are not as full-featured as other minifiers like the popular Yahoo! one.  However, these are linked into DMP because they are pure Python code, and they are incredibly fast.  If you want more complete minification, this probably isn't it.  

These two modules might be simplistic, but they *are* fast enough to do minification of dynamic `*.jsm` and `*.cssm` files on the fly.  Setting the `DMP_MINIFY_JS_CSS` variable to True will not only minify during the `dmp_collectstatic` command, it will minfiy the dynamic files as well.

Again, if you want to disable these minifications procedures, simply set `DMP_MINIFY_JS_CSS` to False.

Minification of `*.jsm` and `*.cssm` is skipped during development so you can debug your Javascript and CSS.  Even if your set `DMP_MINIFY_JS_CSS` to True, minification only happens when settings.py `DEBUG` is False.
        
        

#### Django Apps + DMP Apps

You might have some traditional Django apps (like the built-in `/admin` app) and some DMP apps (like our `/homepage` in this tutorial).  Your Django apps need the regular `collectstatic` routine, and your DMP apps need the `dmp_collectstatic` routine.

The solution is to run both commands.  Using the options of the two commands, you can either send the output from each command to *two different* static directories, or you can send them to a single directory and let the files from the second command potentially overwrite the files from the first.  I suggest this second method:

        python3 manage.py collectstatic
        python3 manage.py dmp_collectstatic

The above two commands will use both methods to bring files into your `/static/` folder.  You might get some duplication of files, but the output of the commands are different enough that it should work without issues.



## Redirecting with Exceptions

Suppose your view needs to redirect the user's browser to a different page than the one currently being routed.  For example, the user might not be authenticated correctly or a form might have just been submitted.  In the latter case, web applications often redirect the browser to the *same* page after a form submission (and handling with a view), effectively switching the browser from its current POST request to a regular GET request.  That way, if the user hits the refresh button within his or her browser, the page simply gets refreshed without the form being submitted again.

When you need to redirect the browser to a different page, you should normally use the standard `django.http.HttpResponseRedirect` object.  By returning a redirect object from your view, DMP (and subsequently Django) direct the browser to redirect.  

BUT, suppose you are several levels deep in method calls without direct access to the request or response objects?  How can you direct a method several levels up in the call stack to send a redirect response?  That's where the `django_mako_plus.controller.RedirectException` comes in handy.  Since it is an exception, it bubbles all the way up the stack to the DMP router -- where it is sent directly to the browser.

Is this an abuse of exceptions?  Probably.  But in one possible viewpoint, a redirect can be seen as an exception to normal processing.  It is quite handy to be able to redirect the browser from anywhere in your web code.  If this feels dirty to you, feel free to skip ahead to the next section and ignore this part of DMP.  :)

Two types of redirects are supported by DMP: a standard browser redirect and an internal redirect.  The standard browser redirect, `RedirectException`, uses the HTTP 302 code to initiate a new request.  The internal redirect is simpler and shorter: it restarts the routing process with a different view/template within the *current* request, without changing the browser url.  Internal redirect exceptions are rare and shouldn't be abused; an example might be returning an "upgrade your browser" page to a client.  Since the user has an old browser, a regular 302 redirect might not work the way you expect.  Redirecting internally is much safer.

To initiate the two types of redirects, use the following code:

        from django_mako_plus.controller import RedirectException, InternalRedirectException

        # send a normal, browser-based redirect from anywhere in the call stack
        # this is effectively the same as: return django.http.HttpResponseRedirect('/some/new/url')
        raise RedirectException('/some/new/url')
        
        # restart the routing process with a new view, as if the browser had done this url
        # the browser keeps the same url and doesn't know a redirect has happened
        # the next line is as if the browser went to /homepage/upgrade/
        raise RedirectException('homepage.views.upgrade', 'process_request')




# Deployment Recommendations

This section has nothing to do with the Django-Mako-Framework, but I want to address a couple issues in hopes that it will save you some headaches.  One of the most difficult decisions in Django development is deciding how to deploy your system.  In particular, there are several ways to connect Django to your web server: mod_wsgi, FastCGI, etc.

At MyEducator, we've been through all of them at various levels of testing and production.  By far, we've had the best success with [uWSGI](https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/uwsgi/).  It is a professional server, and it is stable.

One other decision you'll have to make is which database use.  I'm excluding the "big and beefies" like Oracle or DB2.  Those with sites that need these databases already know who they are.  Most of you will be choosing between MySQL, PostgreSQL, and perhaps another mid-level database.  

In choosing between these mid-level databases, you'll find that many, if not most, of the Django developers use PostgreSQL.  The system is likely tested best and first on PG.  We started on MySQL, and we moved to PG after experiencing a few problems.  Since deploying on PG, things have been amazingly smooth.

Your mileage may vary with everything in this section.  Do your own testing and take it all as advice only.  Best of luck. 

## Deployment Tutorials

The following links contain tutorials for deploying Django with DMP:

* http://blog.tworivershosting.com/2014/11/ubuntu-server-setup-for-django-mako-plus.html


# DMP Signals

> This is an advanced topic, and it is not required to use DMP.  I suggest you skip this section and come back to it if you ever need Signals.

DMP sends several custom signals through the Django signal dispatcher.  The purpose is to allow you to hook into the router's processing.  Perhaps you need to run code at various points in the process, or perhaps you need to change the request.dmp_* variables to modify the router processing.

Before going further with this section's examples, be sure to read the standard Django signal documentation.  DMP signals are simply additional signals in the same dispatching system, so the following examples should be easy to understand once you know how Django dispatches signals.

## Step 1: Enable DMP Signals

Be sure your settings.py file has the following in it:

        DMP_SIGNALS = True
        
## Step 2: Create a Signal Receiver

The following creates two receivers.  The first is called just before the view's process_request function is called.  The second is called just before DMP renders .html templates.

        from django.dispatch import receiver
        from django_mako_plus.controller import signals

        @receiver(signals.dmp_signal_pre_process_request)
        def dmp_signal_pre_process_request(sender, **kwargs):
     request = kwargs['request']
     console.log('>>> process_request signal received!')
  
        @receiver(signals.dmp_signal_pre_render_template)
        def dmp_signal_pre_render_template(sender, **kwargs):
     request = kwargs['request']
     context = kwargs['context']            # the template variables
     template = kwargs['template']  # the Mako template object that will do the rendering
     console.log('>>> render_template signal received!')

The above code should be in a code file that is called during Django initialization.  Good locations might be in a `models.py` file or your app's `__init__.py` file.

See the `django_mako_plus/controller/signals.py` file for all the available signals you can hook to.

# Where to Now?

This tutorial has been an introduction to the Django-Mako-Plus framework.  The primary purpose of DMP is to combine the excellent Django system with the also excellent Mako templating system.  And, as you've hopefully seen above, this framework offers many other benefits as well.  It's a new way to use the Django system.

I suggest you continue with the following:

* Go through the [Mako Templates](http://www.makotemplates.org/) documentation.  It will explain all the constructs you can use in your html templates.
* Read or reread the [Django Tutorial](http://www.djangoproject.com/). Just remember as you see the tutorial's Django template code (usually surrounded by `{{  }}`) that you'll be using Mako syntax instead (`${  }`).
* Link to this project in your blog or online comments.  I'd love to see the Django people come around to the idea that Python isn't evil inside templates.  Complex Python might be evil, but Python itself is just a tool within templates.


