Django-Style Template Rendering
=====================================

In the `tutorial <tutorial_views.html>`_ , you may have noticed that we didn't use the "normal" Django shortcuts like ``render`` and ``render_to_response``.  DMP provides the shortcuts like ``request.dmp.render`` because its renderers are tied to apps (which is different than Django).

But that doesn't mean you can't use the standard Django shortcuts and template classes with DMP.  As a template engine, DMP conforms to the Django standard.  If you want to use Django's shortcuts and be more standard, here's how to do it.

``render(request, template, context)``
---------------------------------------------------

The following imports only from ``django.shortcuts``:

.. code:: python

    # doin' the django way:
    from django.shortcuts import render
    return render(request, 'homepage/index.html', context)

    # or to be more explicit with Django, you can specify the engine:
    from django.shortcuts import render
    return render(request, 'homepage/index.html', context, using='django_mako_plus')


Specifying the Template Name
-----------------------------------

All right, the above code actually doesn't perfectly match the Django docs.  In normal Django, you'd only specify the filename as simply ``index.html`` instead of ``homepage/index.html`` as we did above.  Django's template loaders look for ``index.html`` in your "template directories" as specified in your settings.  In the case of the ``app_directories`` loader, it even searches the same setup as DMP: the ``app/templates/`` directories.

But unlike DMP, Django searches **all** templates directories, not just the current app.  As it searches through your various ``templates`` folders, it uses the first ``index.html`` file it finds. In other words, it's not really app-aware. In real projects, this often necessitates longer template filenames or additional template subdirectories.  Yuck.

Since app-awareness is at the core of DMP, the template should be specified in the format ``app/template``.  This allows DMP load your template from the right app.


``TemplateResponse`` and ``SimpleTemplateResponse``
---------------------------------------------------------

Django provides two classes that delay template rendering until the last possible moment.  Late rendering allows things like middleware to adjust the template or context before rendering occurs.

To use these classes with DMP, use the file pattern we just discussed: ``app/template``.  Or to be more explicit, get the template object explicitly.  Here are some examples:

.. code:: python

    # using TemplateResponse:
    from django.template.response import TemplateResponse
    return TemplateResponse(request, 'homepage/index.html', context)

    # using SimpleTemplateResponse:
    from django.template.response import SimpleTemplateResponse
    return SimpleTemplateResponse('homepage/index.html', context)

    # using TemplateResponse with an explicit template object:
    from django.template.response import TemplateResponse
    from django_mako_plus import get_template as dmp_get_template
    return TemplateResponse(request, dmp_get_template('homepage', 'index.html'), context)


Further Reading about Template Locations
------------------------------------------

The topic on `Template Location/Import <basics_paths.html>`_ describes the nuances of template directories, inheritance, and discovery.
