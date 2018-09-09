Upgrade Notes
==============================

This document contains upgrade notes for those already using DMP.  We started the document at version 4.3.

5.6 - September, 2018

1. Changed the management command format to the way it used to be.  Sorry for the change, everyone!  Doing subcommands the way we were required tying to internal Django classes.  When Django changed things in 2.1, it broke subcommands. It was going to be quite difficult to support both 2.0 and 2.1 at the same time.  Plus I probably shouldn't have tied to internal stuff more than needed anyway.

So back to old style.  If you previously typed:

python manage.py dmp startapp homepage

you now type:

python manage.py dmp_startapp homepage


5.5 - June, 2018
----------------------------------------

1. The universal ``route_request`` function was removed.  DMP now plugs into Django as a regular URL resolver.  This means the view function is no longer shadowed behind ``route_request`` but is instead directly used.  One benefit of this change is decorators like ``@csrf_exempt`` work now.

This caused a few backwards-compatible changes.  Do a search and replace for the following:

+--------------------------------+-----------------------------------+
| Old                            | New                               |
+================================+===================================+
| `request.dmp.function_obj`     | `request.dmp.callable`            |
+--------------------------------+-----------------------------------+
| `request.dmp.class_obj`        | `request.dmp.callable.view_class` |
+--------------------------------+-----------------------------------+

A new variable, ``request.dmp.view_type`` gives information about the type of view function being rendered.

2. If you are using DMP's built-in ``urls.py`` file --``url('', include('django_mako_plus.urls')),`` -- no other changes are necessary.

If you have custom URLs, you need to change ``re_path`` to ``dmp_path`` in your urls.  See DMP's ``urls.py`` file on GitHub as well as the rewritten Installation section of the docs for an example.

3. Some functions were moved from the template engine to the django_mako_plus app config.  What used to be ``engine.is_dmp_app`` is not ``apps.get_app_config('django_mako_plus').is_registered_app``.


5.4 - May, 2018
----------------------------------------

The converters and ``view_function`` decorator were refactored.  If you're just using the standard DMP system, these changes won't affect you.

If you were using custom converters and/or a custom view_function decorator, see the docs on parameter conversion.



5.3 - April, 2018
----------------------------------------

The DMP management commands have been refactored.  The sass cleanup command is removed.

The remaining commands are now subcommands.  If before you typed ``python3 manage.py dmp_startapp``, now type ``python3 manage.py dmp startapp``.



5.2 - Late March, 2018
----------------------------------------

I continued refactoring the webpack providers and workflow.  While doing this, I updated how DMP calculates the ``version_id`` on static files. It now uses the file modification time PLUS contents checksum.  This method is fast and automatic.

If you are explicitly setting ``version_id`` in your call to links, as in ``${ django_mako_plus.links(self, version_id=...) }``, remove the ``version_id`` parameter.

If you really need to set this, extend the ``JsLinkProvider`` and/or ``CssLinkProvider`` classes with your custom behavior.  It's a very special-case need, so it made sense to automate this for the 99%.



5.1 - March, 2018
----------------------------------------

I refactored the webpack providers and workflow, but I doubt anyone is using them yet.  If you happen to have jumped on this in the past three weeks that 5.0 was out, be sure to read the webpack page and change your settings appropriately.



5.0 - February, 2018
----------------------------------------

1. The DMP options in settings.py has changed a little.  We recommend comparing your settings.py file against the current template (see file django_mako_plus/defaults.py on GitHub).

2. The biggest change is the variables DMP attaches to the request have been moved to an object, available as `request.dmp`.  This causes less namespace pollution of the request and allows easier changes going forward.  The following are the old to new adjustments you may need.  We recommend moving from `urlparams` to automatic view parameter conversion, although this is likely a significant change (there are no plans to remove `urlparams`, so this isn't required).

+--------------------------------+--------------------------------+
| Old                            | New (DMP 4.4)                  |
+================================+================================+
| `request.dmp_router_app`       | `request.dmp.app`              |
+--------------------------------+--------------------------------+
| `request.dmp_router_page`      | `request.dmp.page`             |
+--------------------------------+--------------------------------+
| `request.dmp_router_function`  | `request.dmp.function`         |
+--------------------------------+--------------------------------+
| `request.dmp_router_module`    | `request.dmp.module`           |
+--------------------------------+--------------------------------+
| `request.dmp_router_class`     | `request.dmp.class_obj`        |
+--------------------------------+--------------------------------+
| `request._dmp_router_function` | `request.dmp.function_obj`     |
+--------------------------------+--------------------------------+
| `request.urlparams`            | `request.dmp.urlparams`        |
+--------------------------------+--------------------------------+
| `request.dmp_render`           | `request.dmp.render`           |
+--------------------------------+--------------------------------+
| `request.dmp_render_to_string` | `request.dmp.render_to_string` |
+--------------------------------+--------------------------------+

    *Important:* As noted in the table above, search your codebase for ``request.dmp_render`` and replace with ``request.dmp.render``.

3. Static files (CSS/JS): MakoCssProvider, MakoJsProvider, link_css, link_js, link_template_css, link_template_js are removed.  Instad, use ${ django_mako_plus.links() } once in the <head> section of your base page.

4. RedirectException: Optional parameters 'permanent' and 'as_javascript' are removed.  Use the subclasses by these names instead.

5. SCSS Compiling: The entire sass.py file is removed, including functions check_template_scss, compile_scss_file, compile_scssm_file.  Instead, use the Sass compile provider.  See providers in the static files docs for more information.

6. The named parameters in urls.py has changed.  You only need to adjust your urls.py if you have custom patterns.  For those doing it the normal way (including DMP's urls.py), no change is necessary.

+------------------------+-------------------+
| Old                    | New (DMP 4.4)     |
+========================+===================+
| `dmp_router_app`       | `dmp_app`         |
+------------------------+-------------------+
| `dmp_router_page`      | `dmp_page`        |
+------------------------+-------------------+
| `dmp_router_function`  | `dmp_function`    |
+------------------------+-------------------+
| `urlparams`            | `dmp_urlparams`   |
+------------------------+-------------------+

7. Rendering: render_to_string_shortcut_deprecated and render_to_response_shortcut_deprecated are removed, but this shouldn't affect anyone because they are internal function.



4.3 - November, 2017
----------------------------------------

tl;dr for existing projects:

1. Add ``dmp-common.js`` to your site's base template (add above any DMP calls).

2. Search for ``django_mako_plus.link_css`` and change to ``django_mako_plus.links``.

3. Search for ``django_mako_plus.link_js`` and simply remove.

4. Search for ``django_mako_plus.link_template_css`` and change to ``django_mako_plus.template_links``.

5. Search for ``django_mako_plus.link_template_js`` and remove.

6. (optional) Change deprecated ``.cssm`` files to ``.css`` and ``.jsm`` files to ``.js``.  This one may take some work.  Be sure to read the docs on what needs to be done.

We added provider classes, which creates a customizable system for linking static files.  Default settings for the providers will handle everything for you, but note that you can add ``CONTENT_PROVIDERS`` to your settings file to customize how links are created in templates.

DMP now requires inclusion of `dmp-common.js <https://github.com/doconix/django-mako-plus/tree/master/django_mako_plus/scripts>`_ in your base template(s).  This is included in the base template of new projects, but existing projects need to link to the file.  See the installation guide for more info.

``link_css`` and ``link_js`` functions are deprecated but still work for now.  Your base template should now have a single call to ``django_mako_plus.links(self)`` in the ``<head>`` section.  To switch over, simply replace ``link_css`` with ``links`` and delete the reference to ``link_js``.  Both style and script links are returned by the new function because best practices no longer recommend placing scripts at the end of your page (async/defer in modern browsers make it unnecessary).

In similar fashion, ``link_template_css`` and ``link_template_js`` is now one call to ``template_links``.

``*.cssm`` files are deprecated but still work for now.  Few users seemed to use this.  If you are using them, move the dynamic parts to your templates and convert to a normal css file.

``*.jsm`` files are deprecated but still work for now.  These were of great use to many, but ``jscontext`` gives a new, improved way to do "dynamic" JS.  Convert all ``.jsm`` files to regular ``.js`` files, and follow the pattern given in `the tutorial <tutorial_css_js.html#javascript-in-context>`_.  The new method still allows you to easily send variables to your JS but doesn't need any rendering.  You'll need to convert code in your JS from ``if (${ somebool })`` to ``if (context.somebool)``.  Note that the Mako codes are gone, and the new code is pure JS that uses a context dictionary that exists in the JS namespace.

Compilation of Scss has been moved to a provider class, and a new provider for Less is now available.  In fact, the ``CompileProvider`` can compile any type of file (using the settings in ``CONTENT_PROVIDERS``).  Check out the Transcrypt example in `the topic on CSS and JS <static.html>`_.
