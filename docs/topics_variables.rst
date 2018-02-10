Useful Variables
======================

At the beginning of each request (as part of its middleware), DMP adds a routing data object as ``request.dmp``. This object primarily supports the inner workings of the DMP router, but it may be useful to you as well. The following are available throughout the request:

-  ``request.dmp.app``: The Django application specified in the
   URL. In the URL ``http://www.server.com/calculator/index/1/2/3``,
   ``request.dmp.app`` is the string "calculator".

|

-  ``request.dmp.page``: The name of the Python module specified
   in the URL. In the URL
   ``http://www.server.com/calculator/index/1/2/3``, the
   ``request.dmp.page`` is the string "index". In the URL
   ``http://www.server.com/calculator/index.somefunc/1/2/3``,
   ``request.dmp.page`` is still the string "index".

|

-  ``request.dmp.function``: The name of the function within the
   module that will be called, even if it is not specified in the URL.
   In the URL ``http://www.server.com/calculator/index/1/2/3``, the
   ``request.dmp.function`` is the string "process\_request" (the default
   function). In the URL
   ``http://www.server.com/calculator/index.somefunc/1/2/3``,
   ``request.dmp.function`` is the string "somefunc".

|

-  ``request.dmp.module``: The name of the real Python module
   specified in the URL, as it will be imported into the runtime module
   space. In the URL ``http://www.server.com/calculator/index/1/2/3``,
   ``request.dmp.module`` is the string "calculator.views.index".

|

-  ``request.dmp.class_obj``: The name of the class if the router
   sees that the "function" is actually a class-based view. None
   otherwise.

|

-  ``request.dmp.urlparams``: A list of parameters specified in the URL.
    See the the topic on `Parameter Conversion <topics_converters.html>`__
    for more information.

|

A "default" routing object is added at the beginning of the request, but actual routing data isn't available  **until the view middleware stage**.  It isn't done earlier in the lifecycle because DMP should obey Django's urls.py routing rules (and urls.py comes after the middleware).