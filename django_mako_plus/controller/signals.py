from django.dispatch import Signal


#############################################################
###   Signals that we send from DMP

#  Sent just before DMP calls a view's process_request method
#
#    request :: the request object, which has several attributes that might be of interest:
#                 request.dmp_router_app      :: The app name, based on the current url.
#                 request.dmp_router_page     :: The page name (the views/.py file or templates/.html file), based on the current url.
#                 request.urlparams           :: Any extra url parameters, based on the current url.
#                 request.dmp_router_module   :: The module where the view function is located.
#                 request.dmp_router_function :: The specific view function within the module to call.
#   
dmp_signal_pre_process_request = Signal(providing_args=['request'])

#  Sent just before DMP calls a view's process_request method.
#  If the method returns a different HttpResponse object, the response is replaced with that object.
#
#    request      :: the request object
#    response     :: the return from the process_request method, normally an HttpResponse object.
#
dmp_signal_post_process_request = Signal(providing_args=['request', 'response'])

#  Sent just before DMP renders a Mako template
#
#    request  :: the request object
#    context  :: the dict of variables being sent to the template.
#    template :: the Mako template object that will render.
dmp_signal_pre_render_template = Signal(providing_args=['request', 'context', 'template'])

#  Sent just after DMP renders a Mako template.  
#  If the method returns a value, the template-generated content is replaced with that value.
#
#    request  :: the request object
#    context  :: the dict of variables being sent to the template.
#    template :: the Mako template object that will render.
#    content  :: the rendered content from the template.
dmp_signal_post_render_template = Signal(providing_args=['request', 'context', 'template', 'content'])

#  Send when a RedirectException is encountered in the DMP controller.
#
#    request      :: the request object
#    exc          :: The exception object, including:
#                       exc.redirect_to (new url the router will process with)
#                       exc.permanent   (whether the browser should be told it is a permanent redirect or not)
dmp_signal_redirect_exception = Signal(providing_args=['request', 'exc'])


#  Send when an InternalRedirectException is encountered in the DMP controller.
#
#    request      :: the request object
#    exc          :: The exception object, including exc.redirect_to (new url the router will process with).
dmp_signal_internal_redirect_exception = Signal(providing_args=['request', 'exc'])

