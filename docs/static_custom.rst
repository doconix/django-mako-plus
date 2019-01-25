Creating a Custom Provider
==============================

Suppose you need custom preprocessing of static files or custom template content.  Your future may include creating a new provider class. Fortunately, these are pretty simple classes. Once you create the class, simply reference it in your settings.py file.

.. code-block:: python

    from django_mako_plus import BaseProvider

    class YourCustomProvider(BaseProvider):
        # these default options will be combined with BaseProvider.DEFAULT_OPTIONS and any in settings.py
        DEFAULT_OPTIONS = {
            'any': 'additional',
            'options': 'should',
            'be': 'specified',
            'here': '.',
        }

    def start(self, provider_run, data):
        '''
        Called on the *main* template's provider list as the run starts.
        Initialize values in the data dictionary here.
        '''
        pass

    def provide(self, provider_run, data):
        '''Called on *each* template's provider list in the chain - use provider_run.write() for content'''
        pass

    def finish(self, provider_run, data):
        '''
        Called on the *main* template's provider list as the run finishes
        Finalize values in the data dictionary here.
        '''
        pass

Your provider will be instantitated once for each template in the system. When a template is first rendered at production time, your provider will be instantiated and cached with the template for future use.  This single instance for a template will be used regardless of when the template is rendered -- as an ancestor of another template or as a final template.

Wherever possible, move code to the constructor so the calls to ``start``, ``provide``, and ``finish`` can be as fast as possible.  In particular, ``provide`` is called for the template **and** every supertemplate.

    During development (``DEBUG = True``), providers are instantiated **every** time the template is rendered.  In effect, each render of a template is treated as if it were the "first time".  This allows template/script/css changes to be seen without a server restart.

For More Information
--------------------------

See the ``provider/`` directory of the `DMP source code <https://github.com/doconix/django-mako-plus>`_.
