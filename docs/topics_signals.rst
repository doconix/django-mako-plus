Signals in DMP
===================

DMP sends several custom signals through the Django signal dispatcher. The purpose is to allow you to hook into the router's processing and respond to events that occur in DMP.

    Before going further with this section's examples, be sure to read the standard Django signal documentation. DMP signals are simply additional signals in the same dispatching system, so the following examples should be easy to understand once you know how Django dispatches signals.

Available Signals
-------------------------------

``dmp_signal_pre_process_request``
    Triggered just before DMP calls a view's process_request() method.

``dmp_signal_post_process_request``
    Triggered just after a view's process_request() method returns.

``dmp_signal_pre_render_template``
    Triggered just before DMP renders a Mako template.

``dmp_signal_post_render_template``
    Triggered just after DMP renders a Mako template.

``dmp_signal_redirect_exception``
    Triggered when a RedirectException is encountered in the DMP controller.

``dmp_signal_internal_redirect_exception``
    Triggered when an InternalRedirectException is encountered in the DMP controller.

``dmp_signal_register_app``
    Triggered just after the DMP template engine registers an app as a DMP app (once per app at server start).


See the `function documentation in signals.py <https://github.com/doconix/django-mako-plus/blob/master/django_mako_plus/signals.py>`_ for more information about each signal and its kwargs.


Enabling DMP Signals
---------------------------------

Be sure your settings.py file has the following in it:

.. code-block:: python

    TEMPLATES = [
        {
            'NAME': 'django_mako_plus',
            'BACKEND': 'django_mako_plus.MakoTemplates',
            'OPTIONS': {
                'SIGNALS': True,
                ...
            }
        }
    ]


Signal Receivers
-------------------------------------

The following creates two receivers. The first is called just before the view's process\_request function is called. The second is called just before DMP renders .html templates.

.. code-block:: python

    from django.dispatch import receiver
    from django_mako_plus import signals, get_template_loader

    @receiver(signals.dmp_signal_pre_process_request)
    def pre_process_request(sender, request, view_args, view_kwargs, **kwargs):
        print('>>> process_request signal received!')

    @receiver(signals.dmp_signal_pre_render_template)
    def pre_render_template(sender, request, context, template, **kwargs):
        print('>>> render_template signal received!')
        # let's return a different template to be used - DMP will use this instead of kwargs['template']
        tlookup = get_template_loader('myapp')
        template = tlookup.get_template('different.html')

The above code should be in a code file that is called during Django initialization, such as ``apps.py``.
