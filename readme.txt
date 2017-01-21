This app is a template engine that integrates the excellent Django framework with the also excellent Mako templating syntax.  It conforms to the Django API and plugs in as a standard engine.

Please visit https://github.com/doconix/django-mako-plus or open the readme.md file.

1. DMP uses the **Mako templating engine** rather than the weaker Django templating engine.  Why would I want to learn a whole new language for templating when Mako uses my favorite language: Python?

2. DMP allows **calling views and html pages by convention** rather than specific entries in urls.py. Any .html file on your site can be called without new entries in urls.py for every. single. new. page.  Doesn't Python favor convention over configuration?

3. DMP introduces the idea of URL parameters.  These allow you to embed parameters in urls, Django style--meaning you can use pretty URLs like http://myserver.com/abc/def/123/ **without explicit entries in urls.py** and without the need for traditional (i.e. ulgy) ?first=abc&second=def&third=123 syntax.

4. DMP separates view functions into different files rather than all-in-one style.  Anyone who has programmed Django long knows that the single views.py file in each app often gets looooonnng.  Splitting logic into separate files keeps things more orderly.

5. Optionally, DMP automatically includes CSS and JS files, and it allows Python code within these files.  These static files get included in your web pages without any explicit declaration of `<link>` or `<script>` elements.  This means that `mypage.css` and `mypage.js` get linked in `mypage.html` automatically.  Python code within these support files means your CSS can change based on user or database entries.

6. Optionally, DMP integrates with Sass by automatically running `scss` on updated .scss files.

DMP can be used alongside regular Django templates, Jinja2 templates, and other third-party apps.  It plugs in via the regular `urls.py` mechanism, just like any other view.  Be assured that it plays nicely with the other children.

DMP was developed at MyEducator.com, but it has been used in many places since. It requires Python 3+ and Django 1.8+.

