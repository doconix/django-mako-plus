# Use This If You've Said:

* Why are Django templates weak sauce? Why not just use regular Python in templates?
* Why does Django make me list every. single. page. in urls.py?
* I'd like to include Python code in my CSS and Javascript files.
* My app's views.py file is getting HUGE.  How can I split it intelligently?
  
  
# Description

This app is a front controller that integrates Django with Mako templates, among other things.  Django comes with its own template system, but it's fairly weak (by design).  Mako, on the other hand, is a fantastic template system that allows full Python code within HTML pages. 

This app provides a number of benefits:

1. It uses the Mako templating engine rather than the weaker Django templating engine.  Why would I want to learn a whole new language for templating when Mako uses my favorite language: Python?

2. It allows calling views and html pages by convention rather than specific entries in urls.py. Any .html file on your site can be called without new entries in urls.py for every. single. new. page.  Doesn't Python favor convention over configuration?  

3. It introduces the idea of URL parameters.  These allow you to embed parameters in urls, Django style (but without requiring urls.py definitions). 

4. It separates view functions into different files rather than all-in-one style.  This prevents huge views.py files.

5. It automatically includes CSS and JS files, and it allows Python code within these files.  These static files get connected right into the Mako template inheritance tree.  This is different than Less/Sass because it the variables are rendered per user (the others are typically rendered before uplaod to server).

But don't worry, you'll still get all the Django goodness with ORM, views, forms, etc.


# Installation


1. Prerequisites:
   * Install Python 3+ and ensure you can run "python" at the command prompt.
   * Run `easy_install django` or `pip install django` or otherwise install Django (https://www.djangoproject.com).  This is tested against Django 1.6.
   * Run `easy_install mako` or `pip install mako` or otherwise install Mako (http://www.makotemplates.org).  This is tested against Mako 0.9.
   
2. Install Django-Mako-Plus with `easy_install django-mako-plus` or `pip install django-mako-plus`.
   
3. Create a normal Django project with the typical `python django-admin.py startproject <name>`.  In the tutorial below, I'll assume you called your project `test_dmp`.
  
4. In your new project directories, edit settings.py file:
   * Add `django_mako_plus.controller` to your INSTALLED_APPS:
   
         INSTALLED_APPS = (
             'django.contrib.admin',
             'django.contrib.auth',
             'django.contrib.contenttypes',
             'django.contrib.sessions',
             'django.contrib.messages',
             'django.contrib.staticfiles',
             'django_mako_plus.controller',
         )
         
   * Add `django_mako_plus.controller.router.RequestInitMiddleware` to your MIDDLEWARE CLASSES:
   
         MIDDLEWARE_CLASSES = (
             'django.contrib.sessions.middleware.SessionMiddleware',
             'django.middleware.common.CommonMiddleware',
             'django.middleware.csrf.CsrfViewMiddleware',
             'django.contrib.auth.middleware.AuthenticationMiddleware',
             'django.contrib.messages.middleware.MessageMiddleware',
             'django_mako_plus.controller.router.RequestInitMiddleware',
         )       
         
   * Add a logger to help you debug (optional but highly recommended!):
   
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
   * Add the Django-Mako-Plus settings:   
   
         ###############################################################
         ###   Specific settings for the django_mako_plus app

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
         
5. Add the Django-Mako-Plus router as **the last pattern** in your urls.py file:

          urlpatterns = patterns('',
              ...

              # the django_mako_plus controller handles every request - this line is the glue that connects Mako to Django
              url(r'^.*$', 'django_mako_plus.controller.router.route_request' ),
          ) 
          
6. Change to your project directory, then create a new Django-Mako-Plus app with `python manage.py dmp_startapp <app name>`.  In the tutorial below, I'll assume you called your app `homepage`.
  
7. Follow the tutorial below to see the power of Django-Mako-Plus.


# Tutorial

I assume you've just installed Django-Mako-Plus according to the instructions above.  You should have a `dmp_test` project directory that contains a `homepage` app.  You already have a default page in the new app, so fire up your server with `python manage.py runserver` and go to [http://localhost:8000/homepage/index/](http://localhost:8000/homepage/index/).  

You should see a congratulations page.  If you don't, go back to the installation and walk through the steps again.  If you see the page, it seems you can be trained!  Let's explore the directory structure of your new app:

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

The directories should be fairly self-explanatory.  Put your images in images/, your Javascript in scripts/, your CSS in styles/, your html files in templates/, and your Django views in views/.

There's really not much there yet, so let's start with the two primary html template files: base.htm and index.html.  index.html is pretty simple:

        <%inherit file="base.htm" />

        <%block name="content">
            <div class="content">
              <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
              <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
            </div>
        </%block>

If you are familiar with Django templates, you'll recognize the template inheritance in the `<%inherit/>` tag.  However, this is Mako code, not Django code.  At some point, be sure to head over to the [Mako Templates web site](http://www.makotemplates.org/) and learn its syntax.

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

Pay special attention to the `<%block name="content">` section, which is overridden in `index.html`.  When you create additional pages, simply override this block to place new html into that part of the web page.  The head, page header, and body defined in `base.htm` make the common page parts seen across all pages in your app.

## Routing Without urls.py

In the installation procedures above, you added the following line to your urls.py routing file:

        url(r'^.*$', 'django_mako_plus.controller.router.route_request' ),

The regular expression in this line, `^.*$`, is a wildcard that matches everything.  It tells every url to go to the Django-Mako-Plus router, where it is routed according to the path: /app/page.  For example, the url `/homepage/index/` routes as follows:

* The first url part `homepage` specifies the app that will be used.
* The second url part `index` specifies the view or html page within the app.  In our example:
  * The router first looks for `homepage/views/index.py`.  In this case, it fails because we haven't created it yet.
  * It then looks for `homepage/templates/index.html`.  In our case, it finds the file, so it renders it through the Mako templating engine.
  
The above illustrates the easiest way to show pages.  Simply place .html files in your templates/ directory.  This is useful for pages that don't really need views.  Examples might be the "About Us" and "Terms of Service" pages.  There's usually no functionality or permissions issues with these pages, so no view function is required.

What about the case where a page isn't specified, such as `/homepage/`?  If the url doesn't contain two parts, the router goes to the default page as specified in your settings.py `MAKO_DEFAULT_PAGE` variable.  This allows you to have a "default app" and have pages at the top level of your web server.

If the path is entirely empty (i.e. http://www.yourserver.com/ with *no* path parts), the router uses both defaults specified in your settings.py file: `MAKO_DEFAULT_PAGE` and `MAKO_DEFAULT_APP`.

## Adding a View Function

Let's add some dynamic behavior by adding the current server time to the index page.  Create a new file `homepage/views/index.py` and copy this code into it:

        from django.conf import settings
        from django_mako_plus.controller.router import MakoTemplateRenderer
        from datetime import datetime

        templater = MakoTemplateRenderer('homepage')

        def process_request(request):
          template_vars = {
            'now': datetime.now(),
          }
          return templater.render_to_response(request, 'index.html', template_vars)
  
Reload your server and browser page, and you should see the exact same page.  If you enabled the logger in the installation, you should see the following in your console:

          DEBUG controller :: processing: app=homepage, page=index, funcname=, urlparams=['']
          DEBUG controller :: calling view function homepage.views.index.process_request
          DEBUG controller :: rendering template .../dmptest/homepage/templates/index.html  

These debug statements are incredibly helpful in figuring out why pages aren't routing right.  If your page didn't load right, you'll probably see why in these statements.  In my log above, the first line lists what the controller assigned the app and page to be.

The second line tells me the controller found my new `index.py` view, and it called the `process_request` function successfully.  This is important -- view modules **must** have a `process_request` function.  This is done for security.  If the framework let browsers specify any old function, end users could invoke any function of any module on your system!  By hard coding the name `process_request`, the framework limits end users to one specifically-named function.

> Later in the tutorial, we'll describe another way to call a function by prefixing any name with `process_request__`.  So in reality, you can actually have multiple, callable functions in a module.  But they all must start with the hard-coded `process_request`.

Within our `process_request` method, we explicitly call the Mako renderer with the name of the html file to be rendered.  The template_vars (the third parameter of the call) is a dictionary containing variable names that will be globally available within the template.

Let's use the `now` variable in our index.html template:

        <%inherit file="base.htm" />

        <%block name="content">
            <div class="content">
              <h3>Congratulations -- you've successfully created a new django-mako-plus app!</h3>
              <h4>Next Up: Go through the django-mako-plus tutorial and add Javascript, CSS, and urlparams to this page.</h4>
              <p class="time">The current server time is ${ now }.</p>
            </div>
        </%block>

The `${ varname }` syntax is Mako and is described more fully on the Mako web site.  Right now, it's most important that you see how to send data from the view to the template.  If you already know Django templates, it's pretty close to the same pattern.  The Django-Mako-Framework tries to improve Django, but with minimal changes in patterns.

Reload your web page and ensure the new view is working correctly.


## URL Parameters

Django is all about pretty urls.  In keeping with that philosophy, this framework has URL parameters.  We've already used the first two items in the path: the first specifies the app, the second specifies the view/template.  URL parameters are the third part, fourth part, and so on.

In most web apps, you'd specify parameters using key=value pairs, as in /homepage/index?first=abc&second=def.  That's ugly, of course, and it's certainly not the Django way.

With this framework, you'd instead specify parameters as /homepage/index/abc/def/.  The controller makes them available to your view as `request.urlparams[0]` and `request.urlparams[1]`.  

Suppose you have a product detail page that needs the SKU number of the product to display.  A nice way to call that page might be `/catalog/product/142233342/`.  The app=catalog, view=product.py, and urlparams[0]=142233342.

Note that URL parameters don't take the place of form parameters.  You'll still use GET and POST parameters to submit forms.  URL parameters are best used for object ids and other simple items that pages need to display. 

Suppose we want to display our server time with user-specified format.  We might present several different `<a href>` links to the user that contain different formats.  The following change to index.py uses the specified format for the date:
  
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

* The default format: http://localhost:8000/homepage/index/
* The current hour: http://localhost:8000/homepage/index/%H/
* The month, year: http://localhost:8000/homepage/index/%B,%20%Y

If a urlparam doesn't exist, it always returns the empty string ''.  This is slightly different than a regular Python list, which throws an exception when an index is too large.  This means that request.urlparams[50] returns the empty string rather than an exception.  The `if` statement in the code above can be used to determine if a urlparam exists or not.  Another way to code a default value for a urlparam is `request.urlparam[2] or 'some default value'`.  


## A Bit of Style

Modern web pages are made up of three primary parts: html, CSS, and Javascript.  Since your pages all need these three components, this framework combines them for you.  All you have to do is name the .html, the css., and the .js file with the same name.

To style our index.html file, create the new file `homepage/styles/index.css` and copy the following into it:

        .time {
          font-size: 2em;
          color: red;
        }

When you refresh your page, the server time should be large, red text.  If you view the html source in your browser, you'll see a new `<link...>` to the index.css file.  That's all there is too it.  Name the file the same and place in the styles/ directory, and it will automatically be linked.

> Note the big number after the link in the html source.  That's the server start time, in minutes since 1970.  This is included because browsers (especially Chrome) don't automatically download new CSS files.  They use their cached versions until a specified date. By adding a number to the end of the file, the browsers will think the CSS files are new whenever you restart your server.  Whenever you need to send CSS changes to clients and have them ignore their caches, simply restart your server!

## A Bit of Style, Reloaded

The style of a web page is often dependent upon the user, such as a theme on an online email app.  Django-Mako-Plus supports this, too!  You can use Mako (hence, any Python code) not only in your .html files, but also in your CSS and JS files.  Simply name the file with `.cssm` rather than .css.  When the framework sees `index.cssm`, it runs the file through the Mako templating engine before it sends it out.

> Since we assume .cssm files are generated per user, they are embedded directly in the HTML rather than linked.  This circumvents a second call to the server, which would happen every time since the CSS is being dynamically generated.

Let's make the color dynamic by adding a new random variable to our index.py view:

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

        .time {
          font-size: 2em;
          color: ${ timecolor };
        }
  
Refresh your browser a few times.  The color should change with each refresh!

> Note that this behavior is different than CSS engines like Less and Sass. Most developers use Less and Sass for variables at development time.  These variables are rendered and stripped out before upload to the server, and they become static, normal CSS files on the server.  .cssm files should be used for dynamically-generated, per-request CSS.


NOT DONE!  WILL CONTINUE LATER.

extending across apps
static location
logging
settings middleware
settings apps
urls.py





# AUTHOR

This app was developed at MyEducator.com.  It is maintained by Conan C. Albrecht <ca@byu.edu>.  You can view my blog at http://warp.byu.edu/.