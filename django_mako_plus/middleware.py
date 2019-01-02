
# try to import MiddlewareMixIn (Django 1.10+)
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # create a dummy MiddlewareMixin if older Django
    MiddlewareMixin = object

from .router import RequestViewWrapper, RoutingData




##########################################################
###   Middleware the prepares the request for
###   use with the controller.


class RequestInitMiddleware(MiddlewareMixin):
    '''
    A required middleware class that adds a RoutingData object to the request
    at the earliest possible moment.

    Note that VIEW middleware functions can not only read the RouteData variables, but they can
    adjust values as well. This power should be used with great responsibility, but it allows
    middleware to adjust the app, page, function, and url params if needed.
    '''
    # This singleton is set on the request object early in the request (during middleware).
    # Once urls.py has processed, request.dmp is changed to a populated RoutingData object.
    INITIAL_ROUTING_DATA = RoutingData()


    def process_request(self, request):
        request.dmp = self.INITIAL_ROUTING_DATA

    def process_view(self, request, view_func, view_args, view_kwargs):
        # view_func will be a RequestViewWrapper when our resolver (DMPResolver) matched
        if isinstance(view_func, RequestViewWrapper):
            view_func.routing_data.request = request
            request.dmp = view_func.routing_data
