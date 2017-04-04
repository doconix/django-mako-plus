About DMP
===========

This app is a template engine that integrates the excellent Django
framework with the also excellent Mako templating syntax. It conforms to
the Django API and plugs in as a standard engine.

1. DMP uses the **Mako templating engine** rather than the weaker Django
   templating engine. Why would I want to learn a whole new language for
   templating when Mako uses my favorite language: Python?

2. DMP allows **calling views and html pages by convention** rather than
   specific entries in urls.py. Any .html file on your site can be
   called without new entries in urls.py for every. single. new. page.
   Doesn't Python favor convention over configuration?

3. DMP introduces the idea of URL parameters. These allow you to embed
   parameters in urls, Django style--meaning you can use pretty URLs
   like http://myserver.com/abc/def/123/ **without explicit entries in
   urls.py** and without the need for traditional (i.e. ulgy)
   ?first=abc&second=def&third=123 syntax.

4. DMP separates view functions into different files rather than
   all-in-one style. Anyone who has programmed Django long knows that
   the single views.py file in each app often gets looooonnng. Splitting
   logic into separate files keeps things more orderly.

5. Optionally, DMP automatically includes CSS and JS files, and it
   allows Python code within these files. These static files get
   included in your web pages without any explicit declaration of
   ``<link>`` or ``<script>`` elements. This means that ``mypage.css``
   and ``mypage.js`` get linked in ``mypage.html`` automatically. Python
   code within these support files means your CSS can change based on
   user or database entries.

6. Optionally, DMP integrates with Sass by automatically running
   ``scss`` on updated .scss files.


    **Author's Note:** Django comes with its own template system, but it's
    fairly weak (by design). Mako, on the other hand, is a fantastic
    template system that allows full Python code within HTML pages. The
    primary reason Django doesn't allow full Python in its templates is
    the designers want to encourage you and I to keep template logic
    simple. I fully agree with this philosophy. I just don't agree with
    the "forced" part of this philosophy. The Python way is rather to
    give freedom to the developer but train in the correct way of doing
    things. Even though I fully like Python in my templates, I still
    keep them fairly simple. Views are where your logic goes.