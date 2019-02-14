Adding a New Type
=================================

It's easy to add converter functions for new, specialized types.

    Remember that DMP already knows how to convert all of your models -- you probably don't need to add new converter functions for specific model classes.

Suppose we want to use geographic locations in the format "20.4,-162.0".  The URL might looks something like this:

``http://localhost:8000/homepage/index/20.4,-162.0/``


Let's place our new class and converter function in ``homepage/apps.py`` (you can actually place these in any file that loads with Django). Decorate the function with ``@parameter_converter``, with the type(s) as arguments.

.. code-block:: python

    from django.apps import AppConfig
    from django_mako_plus import parameter_converter

    class HomepageConfig(AppConfig):
        name = 'homepage'


    class GeoLocation(object):
        def __init__(self, latitude, longitude):
            self.latitude = latitude
            self.longitude = longitude

    @parameter_converter(GeoLocation)
    def convert_geo_location(value, parameter):
        parts = value.split(',')
        if len(parts) < 2:
            raise ValueError('Both latitude and longitude are required')
        # the float constructor will raise ValueError if invalid
        return GeoLocation(float(parts[0]), float(parts[1]))

The function must do one of the following:

1.  Return the converted type.
2.  Raise one of these exceptions:

    *  ``ValueError``, which triggers the Http 404 page. This should be done for "expected" conversion errors (e.g. bad data in url).
    *  DMP's ``RedirectException`` or ``InternalRedirectException``.
    *  Any other exception, which triggers the Http 500 page. This should be done for unexpected errors.

When Django starts up, the ``parameter_converter`` decorator registers our new function as a converter.


Using the New Type
--------------------------

In ``homepage/views/index.py``, use our custom ``GeoLocation`` class as the type hint in the index file.

.. code-block:: python

    from homepage.apps import GeoLocation

    @view_function
    def process_request(request, loc:GeoLocation):
        print(loc.latitude)
        print(loc.longitude)
        return request.dmp.render('index.html', {})

Then during each request, DMP reads the signature on ``process_request``, looks up the ``GeoLocation`` type, and calls our function to convert the string to a GeoLocation object.
