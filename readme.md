# Use This If You've Said:

* Why are Django templates weak sauce? Why not just use regular Python in templates?
* Why does Django make me list every. single. page. in urls.py?
* I'd like to include Python code in my CSS and Javascript files.
* My app's views.py file is getting HUGE.  How can I split it intelligently?
  
  
# Description

This app is a front controller that integrates the excellent Django framework with the also excellent Mako templating engine.  Django comes with its own template system, but it's fairly weak (by design).  Mako, on the other hand, is a fantastic template system that allows full Python code within HTML pages. But the framework doesn't stop there (that's the "plus" part of the name).  Django-Mako-Plus adds the following features:

1. DMP uses the Mako templating engine rather than the weaker Django templating engine.  Why would I want to learn a whole new language for templating when Mako uses my favorite language: Python?

2. DMP allows calling views and html pages by convention rather than specific entries in urls.py. Any .html file on your site can be called without new entries in urls.py for every. single. new. page.  Doesn't Python favor convention over configuration?  

3. DMP introduces the idea of URL parameters.  These allow you to embed parameters in urls, Django style (but without requiring urls.py definitions). 

4. DMP separates view functions into different files rather than all-in-one style.  Anyone who has programmed Django long knows that the single views.py file in each app often gets looooonnng.  Splitting logic into separate files keeps things more orderly.

5. DMP automatically includes CSS and JS files, and it allows Python code within these files.  These static files get included in your web pages without any explicit declaration of `<link>` or `<script>` elements.  Python code within these support files means your CSS can change based on user or database entries.

But don't worry, you'll still get all the Django goodness with its fantastic ORM, views, forms, etc.

> The primary reason Django doesn't allow full Python in its templates is the designers want to encourage you and I to keep template logic simple.  I fully agree with this philosophy.  I just don't agree with the "forced" part of this philosophy.  The Python way is rather to give freedom to the developer but train in the correct way of doing things.  Even though I fully like Python in my templates, I still keep them fairly simple.  Views are where your logic goes.


# Installation


### Prerequisites:
* Install Python 3+ and ensure you can run "python" at the command prompt.
* Install Django and Mako.  DMP is currently tested with Django 1.6 and Mako 0.9.

  Easy install method:
  
        easy_install django
        easy_install mako
        
  or PIP method:
  
        pip install django
        pip install mako
   
### Install Django-Mako-Plus

Easy install method:

         easy_install django-mako-plus
         
or PIP method:

         pip install django-mako-plus
   
### Create a Django project

Create a Django project with the typical:

        python django-admin.py startproject <name>
  
This step is described in detail in the standard Django tutorial.  In the sections below, I'll assume you called your project `test_dmp`.
  
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
         
4. Add the Django-Mako-Plus settings:   
   
         ###############################################################
         ###   Specific settings for the Django-Mako-Plus app

         # the default app/templates/ directory is always included in the template search path
         # define any additional search directories here - this allows inheritance between apps
         # absolute paths are suggested
         MAKO_TEMPLATES_DIRS = [ 
           # os.path.join(BASE_DIR, 'base_app', 'templates'),
         ]

         # identifies where the Mako template cache will be stored, relative to each app
         MAKO_TEMPLATES_CACHE_DIR = 'cached_templates/'

         # the default app and page to render in Mako when the url is too short
         MAKO_DEFAULT_PAGE = 'index'  
         MAKO_DEFAULT_APP = 'homepage'

         # these are included in every template by default - if you put your most-used libraries here, you won't have to import them exlicitly in templates
         MAKO_DEFAULT_TEMPLATE_IMPORTS = [
           'import os, os.path, re',
         ]

         ###  End of settings for the base_app Controller
         ################################################################
         
### Enable the Django-Mako-Plus Router

Add the Django-Mako-Plus router as **the last pattern** in your urls.py file:

          urlpatterns = patterns('',
          
              ...

              # the django_mako_plus controller handles every request - this line is the glue that connects Mako to Django
              url(r'^.*$', 'django_mako_plus.controller.router.route_request' ),
          ) 
          
### Create a DMP-Style App

Change to your project directory in the terminal/console, then create a new Django-Mako-Plus app with the following:

        python manage.py dmp_startapp <app name>`
        
In the sections below, I'll assume you called your app `homepage`.
  
Congratulations.  You're ready to go!


# Tutorial

I assume you've just installed Django-Mako-Plus according to the instructions above.  You should have a `dmp_test` project directory that contains a `homepage` app.  You already have a default page in the new app, so fire up your server with `python manage.py runserver` and go to [http://localhost:8000/homepage/index/](http://localhost:8000/homepage/index/).  

You should see a congratulations page.  If you don't, go back to the installation section and walk through the steps again.  Your console might have valuable error message to help troubleshoot things.  

Let's explore the directory structure of your new app:

        homepage/
            __init__.py
            images/
            scripts/
            styles/
            templates/
                base_ajax.htm
                base.htm
                index.html
            views/
                __init__.py

The directories should be fairly self-explanatory, although note they are **different** than a traditional Django app structure.  Put images in images/, Javascript in scripts/, CSS in styles/, html files in templates/, and Django views in views/.

There's really not much there yet, so let's start with the two primary html template files: `base.htm` and `index.html`.  `index.html` is pretty simple:

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

What about the case where a page isn't specified, such as `/homepage/`?  If the url doesn't contain two parts, the router goes to the default page as specified in your settings.py `MAKO_DEFAULT_PAGE` variable.  This allows you to have a "default page", similar to the way web servers default to the index.html page.

If the path is entirely empty (i.e. http://www.yourserver.com/ with *no* path parts), the router uses both defaults specified in your settings.py file: `MAKO_DEFAULT_PAGE` and `MAKO_DEFAULT_APP`.

## Adding a View Function

Let's add some "work" to the process by adding the current server time to the index page.  Create a new file `homepage/views/index.py` and copy this code into it:

        from django.conf import settings
        from django_mako_plus.controller.router import MakoTemplateRenderer
        from datetime import datetime

        templater = MakoTemplateRenderer('homepage')

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

The second line tells me the controller found my new `index.py` view, and it called the `process_request` function successfully.  This is important -- view modules **must** have a `process_request` function.  It's hard coded into the DMP framework.

>This hard coding is done for security.  If the framework let browsers specify any old function, end users could invoke any function of any module on your system!  By hard coding the name `process_request`, the framework limits end users to one specifically-named function.

> Later in the tutorial, we'll describe another way to call a function by prefixing any name with `process_request__`.  So in reality, you can actually have multiple, callable functions in a module.  But they all must start with the hard-coded `process_request`.

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

The `${ varname }` code is Mako syntax and is described more fully on the Mako web site.  Right now, it's most important that you see how to send data from the view to the template.  If you already know Django templates, it's pretty close to the same pattern.  The Django-Mako-Framework tries to improve Django, but with minimal changes in patterns.

Reload your web page and ensure the new view is working correctly.  You should see the server time printed on the screen.  Each time you reload the page, the time should change.

> You might be wondering about the incomplete sentence under the .browser_time paragraph.  Just hold tight.  We'll be using this later in the tutorial.


## URL Parameters

Django is all about pretty urls.  In keeping with that philosophy, this framework has URL parameters.  We've already used the first two items in the path: the first specifies the app, the second specifies the view/template.  URL parameters are the third part, fourth part, and so on.

In traditional web links, you'd specify parameters using key=value pairs, as in /homepage/index?first=abc&second=def.  That's ugly, of course, and it's certainly not the Django way (it does still work, though).

With DMP, you have another, better option available.  You'll specify parameters as /homepage/index/abc/def/.  The controller makes them available to your view as `request.urlparams[0]` and `request.urlparams[1]`.  

Suppose you have a product detail page that needs the SKU number of the product to display.  A nice way to call that page might be `/catalog/product/142233342/`.  The app=catalog, view=product.py, and urlparams[0]=142233342.

These prettier links are much friendlier when users bookmark, include in emails, and write them down.  It's all part of coding a user-friendly web site.

Note that URL parameters don't take the place of form parameters.  You'll still use GET and POST parameters to submit forms.  URL parameters are best used for object ids and other simple items that pages need to display. 

Although this might not be the best use of urlparams, suppose we want to display our server time with user-specified format.  On a different page of our site, we might present several different `<a href>` links to the user that contain different formats (we wouldn't expect users to come up with these urls on their own -- we'd create links for the user to click on).  Change your `index.py` file to use a url-specified format for the date:
  
        from django.conf import settings
        from django_mako_plus.controller.router import MakoTemplateRenderer
        from datetime import datetime

        templater = MakoTemplateRenderer('homepage')

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

Modern web pages are made up of three primary parts: html, CSS, and Javascript (images might be a fourth, but we'll go with three for this discussion).  Since all of your pages need these three components, this framework combines them intelligently for you.  All you have to do is name the .html, the css., and the .js file with the same name, and DMP will automatically generate the `<link>` and `<script>` tags for you.  It will even put them in the "right" spot in the html (styles at the beginning, scripts at the end).

To style our index.html file, create `homepage/styles/index.css` and copy the following into it:

        .server-time {
          font-size: 2em;
          color: red;
        }

When you refresh your page, the server time should be styled with large, red text.  If you view the html source in your browser, you'll see a new `<link...>` near the top of your file.  It's as easy as naming the files the same and placing the .css file in the styles/ directory.

> You might be wondering about the big number after the html source `<link>`.  That's the server start time, in minutes since 1970.  This is included because browsers (especially Chrome) don't automatically download new CSS files.  They use their cached versions until a specified date, often far in the future. By adding a number to the end of the file, browsers will think the CSS files are "new" whenever you restart your server.  Whenever you need to send CSS changes to clients and have them ignore their caches, simply restart your server!  Trixy browsserrs...

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
        from django_mako_plus.controller.router import MakoTemplateRenderer
        from datetime import datetime
        import random

        templater = MakoTemplateRenderer('homepage')

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

As shown in the example above, the template_var dictionary sent the templating engine in `process_request` are globally available in .html, .cssm, and .jsm files.

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

What would the modern web be without Ajax?  Well, truthfully, a lot simpler. :)  In fact, if we reinvented the web with today's requirements, we'd probably end up at a very different place than our current web. Even the name ajax implies the use of xml -- most ajax calls return json or html. :) 

But regardless of web history, ajax is required on most pages today.  I assume you understand the basics of ajax and focus specifically on the ways this framework supports it.

Suppose we want to reload the server time every 5 seconds, but we don't want to reload the entire page.  Let's start with the client side of things.  Let's place a refresh button in `homepage/templates/index.html`:

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
          // update the time every 1 seconds
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
        from django_mako_plus.controller.router import MakoTemplateRenderer
        from datetime import datetime
        import random

        templater = MakoTemplateRenderer('homepage')

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

All right, there **is** a shortcut, and a good one at that. The last section showed you how to create an ajax endpoint view.  Since modern web pages have many little ajax calls thoughout their pages, the framework allows you to put several process_request() methods **in the same .py file**.  

Let's get rid of `homepage/views/index_time.py`.  That's right, just delete the file.

Open `homepage/views/index.py` and add the following to the end of the file:

        def process_request__gettime(request):
          template_vars = {
            'now': datetime.now(),
          }
          return templater.render_to_response(request, 'index_time.html', template_vars)  

Note the name of this new function is `process_request__time`, and it contains the function body from our now-deleted `index_time.py`.  The framework recognizes **any** function that starts with `process_request...` as available endpoints for urls.  Since getting the server time is essentially "part" of the index page, it makes sense to put the ajax endpoint right in the same file.  Both `process_request` and `process_request__time` serve content for the `/homepage/index/` html page.

To take advantage of this new function, let's modify the url in `homepage/scripts/index.jsm`:

        // update button
        $('#server-time-button').click(function() {
          $('.server-time').load('/homepage/index__gettime');
        });

The url now points to `index__gettime`, which the framework translates to `index.py -> process_request__gettime()`.  Just as before, `process_request` is hard coded into the function name so users can't call any function in your codebase.  Only methods that start with `process_request` can be called.

Reload your browser page, and the button should still work.  Press it a few times and check out the magic.

> Since ajax calls often return JSON, XML, or simple text, you often only need to add a `process_request__something()` to your view.  At the end of the function, simply `return HttpResponse("json or xml or text")`.  You likely don't need full template, css, or js files.


## Template Extension Across Apps

You may have noticed that this tutorial has focused on a single app.  Most projects consist of many apps.  For example, a sales site might have an app for user management, an app for product management, and an app for the catalog and sales/shopping-cart experience.  All of these apps probably want the same look and feel, and all of them likely want to extend from the **same** `base.htm` file.

When you run `python manage.py dmp_startapp <appname>`, you get **new** `base.htm` and `base_ajax.htm` filess each time.  This is done to get you started on your first app.  On your second, third, and subsequent apps, you probably want to delete these starter files and instead extend your templates from the `base.htm` and `base_ajax.htm` files in your first app.
  
In fact, in my projects, I usually create an app called `base_app` that contains the common `base.htm` html code, site-wide CSS, and site-wide Javascript.  Subsequent apps simply extend from `base_app/templates/base.htm`.  The common `base_app` doesn't really have end-user templates in it -- they are just supertemplates that support other, public apps.

Unfortunately, doing this isn't as clean as you might expect because the Mako engine disallows inheritance with relative paths.  Suppose I have the following app structure:

        dmptest
            base_app/
                __init__.py
                images/
                scripts/
                styles/
                templates/
                    site_base_ajax.htm
                    site_base.htm
                views/
                    __init__.py
            homepage/
                __init__.py
                images/
                scripts/
                styles/
                templates/
                    index.html
                views/
                    __init__.py

I want `homepage/templates/index.html` to extend from `base_app/templates/site_base.htm`.  The following code in `index.html` is likely what you'd expect, **but it doesn't work**:

        <%inherit file="../../base_app/templates/site_base.htm" />

Since Mako doesn't allow this type of relative referencing, the `MAKO_TEMPLATES_DIRS` variable is included in settings.py.  This variable equals a list of directories that contain **global** templates that can be referenced directly from any app on your site.  To include the `base_app/` app above, we'd set this variable as follows:

        MAKO_TEMPLATES_DIRS = [ 
           os.path.join(BASE_DIR, 'base_app', 'templates'),
        ]

Then in `index.html`, we'd reference the file like this:

        <%inherit file="site_base.htm" />

No paths, either absolute or relative, are required on the `site_base.htm` file pointer.  The `base_app` templates directory is global across your entire project.

You may have noticed that I've renamed the file from `base.htm` to `site_base.htm`.  Since this name is now global to all templates on the site, I've used a name that is not likely to conflict with other template names on the site.  

> In fact, my pages are often three inheritance levels deep: `base_app/templates/site_base.htm -> homepage/templates/base.htm -> homepage/templates/index.html` to provide for site-wide page code, app-wide page code, and specific page code.

Again, this global referencing of templates isn't as clean as I'd like it to be, but it's a limitation of the Mako engine.  Such is life.

> The Mako project actually used to allow relative inheritance.  It was disallowed for a very good reason.  So I'm not really faulting the library -- I'm just stating the limitation.


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

There may be some modules, such as `re` or `decimal` that are so useful you want them available in every template of your site.  In settings.py, simply add these to the `MAKO_DEFAULT_TEMPLATES_IMPORTS` variable:

        MAKO_DEFAULT_TEMPLATE_IMPORTS = [
          'import os, os.path, re',
          'from decimal import Decimal',
        ]

Any entries in this list will be automatically included in templates throughout all apps of your site.  With the above imports, you'll be able to use `re` and `Decimal` and `os` and `os.path` anywhere in any .html, .cssm, and .jsm file.


## Collecting Static Files

Static files are files linked into your html documents like `.css` and `.js` as well as images files like `.png` and `.jpg`.  These are served directly by your web server (Apache, Nginx, etc.) rather than by Django because they don't require any processing.  They are just copied across the Internet.  Serving static files is what web servers were written for, and they are better at it than anything else.

Web servers can be set to directly serve files under a certain directory.  For example, any url starting with `/static/` might be served by Nginx, while the Django framework serves anything else.  Your job is to collect all your image, CSS, and JS files under this single directory.

You could program your site with this structure, but it's easier to develop with all the resources underneath the app they are part of instead of splitting them with an entirely different directory tree that starts with `/static/`.

Django comes with a manage.py command `collectstatic` that creates this /static/ directory for you.  It copies all your static resource files into this subtree so you can easily place them on your web server.  Be sure to read about this capability in the Django documentation.

The Django-Mako-Plus framework has a different layout than traditional Django, so it comes with its own static collection function.  When you are ready to publish your web site, run the following:

        python manage.py dmp_collectstatic
        
TODO: This isn't quite done yet.



## Where to Now?

This tutorial has been an introduction to the Django-Mako-Plus framework.  The primary purpose of DMP is to combine the excellent Django system with the also excellent Mako templating system.  And, as you've hopefully seen above, this framework offers many other benefits as well.  It's a new way to use the Django system.

I suggest you continue with the following:

* Go through the [Mako Templates](http://www.makotemplates.org/) documentation.  It will explain all the constructs you can use in your html templates.
* Read or reread the [Django Tutorial](http://www.djangoproject.com/). Just remember as you see the tutorial's Django template code (usually surrounded by `{{  }}`) that you'll be using Mako syntax instead (`${  }`).
* Link to this project in your blog or online comments.  I'd love to see the Django people come around to the idea that Python isn't evil inside templates.  Complex Python might be evil, but Python itself is just a tool within templates.



# AUTHOR

This app was developed at MyEducator.com.  It is maintained by Dr. Conan C. Albrecht <ca@byu.edu>.  You can view my blog at http://warp.byu.edu/.  Please email me if you find errors with this tutorial or have suggestions/fixes for the DMP framework.
