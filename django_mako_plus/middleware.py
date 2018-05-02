
# try to import MiddlewareMixIn (Django 1.10+)
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # create a dummy MiddlewareMixin if older Django
    MiddlewareMixin = object

from .router import RoutingData
from .util import DMP_OPTIONS


##########################################################
###   Middleware the prepares the request for
###   use with the controller.


class RequestInitMiddleware(MiddlewareMixin):
    '''
    Adds several fields to the request that our controller needs.
    Projects can customize the variables with view middleware that runs after this class.

    This class must be included in settings.py -> MIDDLEWARE.
    '''
    def process_request(self, request):
        '''
        Adds stubs for the DMP custom variables to the request object.

        We do this early in the middleware process because process_view() below gets called
        *after* URL resolution.  If an exception occurs before that (a 404, a middleware exception),
        the variables won't be put on the request object.  Therefore, we put stubs on it at the
        earliest possible place so they exist even if we don't get to process_view().
        '''
        request.dmp = INITIAL_ROUTING_DATA


    def process_view(self, request, view_func, view_args, view_kwargs):
        '''
        Adds the following to the request object:

            request.dmp.app            The Django application (such as "homepage"), as a string.
            request.dmp.page           The view module (such as "index" for index.py), as a string.
            request.dmp.function       The function within the view module to be called (usually "process_request"),
                                       as a string.
            request.dmp.module         The module path in Python terms (such as homepage.views.index), as a string.
            request.dmp.class_obj      The class object, if a class-based view.
            request.dmp.function_obj   The view callable (function, method, etc.) to be called by the router.
            request.dmp.urlparams      A list of the remaining url parts, as a list of strings.
                                       View function parameter conversion uses the values in this list.

        As view middleware, this function runs just before the router.route_request is called.
        '''
        # ensure this hasn't run twice (such as having it in the middleware twice)
        if request.dmp is not INITIAL_ROUTING_DATA:
            return

        # create the RoutingData object
        request.dmp = RoutingData(
            request,
            view_kwargs.pop('dmp_app', None) or DMP_OPTIONS['DEFAULT_APP'],
            view_kwargs.pop('dmp_page', None) or DMP_OPTIONS['DEFAULT_PAGE'],
            view_kwargs.pop('dmp_function', None),
            view_kwargs.pop('dmp_urlparams', '').strip(),
        )



# This singleton is set on the request object early in the request (during middleware).
# Once urls.py has processed, request.dmp is changed to a populated RoutingData object.
INITIAL_ROUTING_DATA = RoutingData()
