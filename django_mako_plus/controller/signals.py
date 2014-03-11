from django.dispatch import Signal


#############################################################
###   Signals that we send from DMP

#  Sent just before DMP calls a view's process_request method
#
#  At this point, the request object has several attributes at this point:
#    request.dmp_router_app           :: The app name, based on the current url.
#    request.dmp_router_page          :: The page name (the views/.py file or templates/.html file), based on the current url.
#    request.urlparams                :: Any extra url parameters, based on the current url.
#    request.dmp_router_module        :: The module where the view function is located.
#    request.dmp_router_function      :: The specific view function within the module to call.
#   
dmp_signal_process_request = Signal(providing_args=['request'])

#  Sent just before DMP renders a Mako template
#
#    context      :: the dict of variables being sent to the template.
#    template_obj :: the Mako template object that will render.
dmp_signal_render_template = Signal(providing_args=['request', 'context', 'template_obj'])


#  Send when a RedirectException is encountered in the DMP controller.
#
#    exc :: The exception object, including:
#              exc.redirect_to (new url the router will process with)
#              exc.permanent   (whether the browser should be told it is a permanent redirect or not)
dmp_signal_redirect_exception = Signal(providing_args=['request', 'redirect_to'])


#  Send when an InternalRedirectException is encountered in the DMP controller.
#
#    exc :: The exception object, including exc.redirect_to (new url the router will process with).
dmp_signal_internal_redirect_exception = Signal(providing_args=['request', 'exc'])

