Upgrade Notes
==============================

This document contains upgrade notes for those already using DMP.  We started the document at version 4.3.

4.3.1 - November, 2017
-----------------------------

tl;dr: **cssm/jsm are deprecated - convert jsm files to the new jscontext pattern.**

We added provider classes, which creates a customizable system for linking static files.  Default settings for the providers will handle everything for you, but note that you can add ``CONTENT_PROVIDERS`` to your settings file to customize how links are created in templates.

``link_css`` and ``link_js`` functions are deprecated but still work for now.  Your base template should now have a single call to ``django_mako_plus.links(self)`` in the ``<head>`` section.  To switch over, simply replace ``link_css`` with ``links`` and delete the reference to ``link_js``.  Both style and script links are returned by the new function because best practices no longer recommend placing scripts at the end of your page (async/defer in modern browsers make it unnecessary).

In similar fashion, ``link_template_css`` and ``link_template_js`` is now one call to ``template_links``.

``*.cssm`` files are deprecated but still work for now.  Few users seemed to use this.  If you are using them, move the dynamic parts to your templates and convert to a normal css file.

``*.jsm`` files are deprecated but still work for now.  These were of great use to many, but ``jscontext`` gives a new, improved way to do "dynamic" JS.  Convert all ``.jsm`` files to regular ``.js`` files, and follow the pattern given in `the tutorial <tutorial_css_js.html#javascript-in-context>`_.  The new method still allows you to easily send variables to your JS but doesn't need any rendering.  You'll need to convert code in your JS from ``if (${ somebool })`` to ``if (context.somebool)``.  Note that the Mako codes are gone, and the new code is pure JS that uses a context dictionary that exists in the JS namespace. 

Compilation of Scss has been moved to a provider class, and a new provider for Less is now available.  In fact, the ``CompileProvider`` can compile any type of file (using the settings in ``CONTENT_PROVIDERS``).  Check out the Transcrypt example in `the topic on CSS and JS <topics_css_js.html>`_.



