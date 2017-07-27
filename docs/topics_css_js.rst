Rendering CSS and JS
================================

In the `tutorial <tutorial_css_js.html>`_, you learned how to automatically include CSS and JS based on your page name .  
If your page is named ``mypage.html``, DMP will automatically include ``mypage.css``, ``mypage.cssm``, ``mypage.js``, and ``mypage.jsm`` in the page content.  Skip back to the `tutorial <tutorial_css_js.html>`_ if you need a refresher.


Rendering Other Pages
------------------------------

But suppose you need to autorender the JS or CSS from a page *other than the one currently rendering*?  For example, you need to include the CSS and JS for ``otherpage.html`` while ``mypage.html`` is rendering.  This is a bit of a special case, but it has been useful at times.

To include CSS and JS by name, use the following within any template on your site (``mypage.html`` in this example):

::

    ## instead of using self:
    ## ${ django_mako_plus.link_css(self) }
    ##
    ## specify the app and page name:
    ${ django_mako_plus.link_template_css(request, 'homepage', 'otherpage.html', context)

    ...

    ## render the scripts with the same name as this template and its supertemplates
    ## instead of using self:
    ## ${ django_mako_plus.link_js(self) }
    ##
    ## specify the app and page name:
    ${ django_mako_plus.link_template_js(request, 'homepage', 'otherpage.html', context)


Rendering Nonexistent Pages
----------------------------------

This special case is for times when you need the CSS and JS autorendered, but don't need a template for HTML.  The ``force`` parameter allows you to force the rendering of CSS and JS files, even if DMP can't find the HTML file.   Since ``force`` defaults True, the calls just above will render even if the template isn't found.  

In other words, just use the calls as shown above.  Even if ``otherpage.html`` doesn't exist, you'll get ``otherpage.css``, ``otherpage.cssm``, ``otherpage.js``, and ``otherpage.jsm`` in the current page content.


Skipping Duplicates
-------------------------------

In rare cases, static file links ``<link ...>`` can show on a page more than once.  For example, this can happen when you ``<%include />`` a subtemplate within a ``for`` loop.  If that subtemplate contains a ``link_css()`` call, you'll get the same CSS links on each run of the loop.

Generally, the best way to handle this is to refactor your code so the duplicate calls don't occur.  However, if this isn't the right solution in a given situation, you can ask DMP to automatically skip duplicate includes by adding the ``duplicates`` parameter:

::

    ${ django_mako_plus.link_css(self, duplicates=False) }

With the above call, DMP will include only one reference to each filename within a given request.
