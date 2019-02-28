.. _topics_variables:

Metadata about the Request
=====================================

As you saw in the tutorial, DMP adds an object to each request as ``request.dmp``. This object supports the inner workings of the DMP router and provides convenient access to render functions. It also contains routing information for the current request.

    These variables are set during `Django's URL resolution stage <https://www.b-list.org/weblog/2006/jun/13/how-django-processes-request/>`_. That means the variables aren't available during pre-request middleware, but they are set by the time view middleware runs.

Available Variables
------------------------------

``request.dmp.app``
    The Django application specified in the URL. In the URL ``http://www.server.com/calculator/index/1/2/3``, request.dmp.app is the string "calculator".

``request.dmp.page``
    The name of the Python module specified in the URL. In the URL ``http://www.server.com/calculator/index/1/2/3``, request.dmp.page is the string "index". In the URL ``http://www.server.com/calculator/index.somefunc/1/2/3``, request.dmp.page is still the string "index".

``request.dmp.function``
    The name of the function within the module that will be called, even if it is not specified in the URL. In the URL ``http://www.server.com/calculator/index/1/2/3``, request.dmp.function is the string "process\_request" (the default function). In the URL ``http://www.server.com/calculator/index.somefunc/1/2/3``, request.dmp.function is the string "somefunc".

``request.dmp.module``
    The name of the real Python module specified in the URL, as it will be imported into the runtime module space. In the URL ``http://www.server.com/calculator/index/1/2/3``, request.dmp.module is the string "calculator.views.index".

``request.dmp.callable``
    A reference to the view function the url resolved to.s

``request.dmp.view_type``
    The type of view: function (regular view function),  class (class-based view), or template (direct template render).

``request.dmp.urlparams``
    A list of parameters specified in the URL.  These are normally sent to your view functions based on their signatures, but the raw values are available here as a list of strings. See the the topic on `Parameter Conversion <converters.html>`_ for more information.
