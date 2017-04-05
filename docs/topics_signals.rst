Signals
===================

DMP sends several custom signals through the Django signal dispatcher. The purpose is to allow you to hook into the router's processing. Perhaps you need to run code at various points in the process, or perhaps you need to change the request.dmp\_\* variables to modify the router processing.

Before going further with this section's examples, be sure to read the standard Django signal documentation. DMP signals are simply additional signals in the same dispatching system, so the following examples should be easy to understand once you know how Django dispatches signals.

Step 1: Enable DMP Signals
---------------------------------

Be sure your settings.py file has the following in it:

::

    'SIGNALS': True,

Step 2: Create a Signal Receiver
-------------------------------------

The following creates two receivers. The first is called just before the view's process\_request function is called. The second is called just before DMP renders .html templates.

.. code:: python

    from django.dispatch import receiver
    from django_mako_plus import signals, get_template_loader

    @receiver(signals.dmp_signal_pre_process_request)
    def dmp_signal_pre_process_request(sender, **kwargs):
        request = kwargs['request']
        print('>>> process_request signal received!')

    @receiver(signals.dmp_signal_pre_render_template)
    def dmp_signal_pre_render_template(sender, **kwargs):
        request = kwargs['request']
        context = kwargs['context']            # the template variables
        template = kwargs['template']          # the Mako template object that will do the rendering
        print('>>> render_template signal received!')
        # let's return a different template to be used - DMP will use this instead of kwargs['template']
        tlookup = get_template_loader('myapp')
        template = tlookup.get_template('different.html')

The above code should be in a code file that is called during Django initialization. Good locations might be in a ``models.py`` file or your app's ``__init__.py`` file.

See the ``django_mako_plus/signals.py`` file for all the available signals you can listen for.
