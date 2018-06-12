
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
    An optional middleware class that adds a RoutingData object to the request
    at the earliest possible moment.

    tl;dr: You only need this middlware if you want to use `request.dmp` in view middleware
    functions.

    If included in MIDDLEWARE, the following happens:

        1. During initial middleware, request.dmp is set with an empty RoutingData object.
        2. During url resolution, a RoutingData object is created with information from the request
            and is available as request.resolver_match.routing_data.
        3. During view middleware, it is attached to the request:
                request.dmp = request.resolver_match.routing_data
        4. After view middleware, parameter conversion occurs.
        5. It is available throughout view decorators and the view function.

    If not included in MIDDLEWARE, the following happens:

        1. During initial middleware, request.dmp doesn't exist (raises an AttributeError).
        2. During url resolution, a RoutingData object is created with information from the request
            and is available as request.resolver_match.routing_data.
        3. During view middleware, it is still available as request.resolver_match.routing_data,
            but request.dmp still raises AttributeError.
        4. After view middleware, it is attached to the request:
                request.dmp = request.resolver_match.routing_data
            Also, parameter conversion occurs now.
        5. It is available throughout view decorators and the view function.

    Note that view middleware functions can not only read the RouteData variables, but they can
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
