from django.dispatch import Signal


#############################################################
###   Signals that we send from DMP
###
###   See the standard documentation on Django regarding
###   signals.  Also see the DMP documentation on these
###   specific signals.

#  Triggered just before DMP calls a view's process_request() method.
#  If the method returns an HttpResponse object, processing stops and the object is returned to the browser.
#
#    request     :: The request object, which has several attributes that might be of interest:
#                       request.dmp.app      :: The app name, based on the current url.
#                       request.dmp.page     :: The page name (the views/.py file or templates/.html file), based on the current url.
#                       request.dmp.urlparams           :: Any extra url parameters, based on the current url.
#                       request.dmp.module   :: The module where the view function is located.
#                       request.dmp.function :: The specific view function within the module to call.
#    view_args   :: The list of positional arguments to be sent to the view function.
#    view_kwargs :: The dictionary of keyword arguments to be sent to the view function.
#
dmp_signal_pre_process_request = Signal(providing_args=['request', 'view_args', 'view_kwargs'])

#  Triggered just after a view's process_request() method returns.
#  If the method returns an HttpResponse object, the normal response is replaced with that object.
#
#    request      :: The request object
#    response     :: The return from the process_request method, normally an HttpResponse object.
#    view_args    :: The list of positional arguments that was to the view.
#    view_kwargs  :: The dictionary of keyword arguments that was sent to the view function.
#
dmp_signal_post_process_request = Signal(providing_args=['request', 'response', 'view_args', 'view_kwargs'])

#  Triggered just before DMP renders a Mako template
#  If the method returns a different Template object than the one passed into it, the returned on is used.
#  In other words, this signal lets you override any template just before DMP renders it.
#
#    request  :: the request object
#    context  :: the dict of variables being sent to the template.
#    template :: the Mako template object that will render.
dmp_signal_pre_render_template = Signal(providing_args=['request', 'context', 'template'])

#  Triggered just after DMP renders a Mako template.
#  If the method returns a value, the template-generated content is replaced with that value.  While
#  the template still rendered, its content is discarded and replaced with this return.
#
#    request  :: the request object
#    context  :: the dict of variables being sent to the template.
#    template :: the Mako template object that will render.
#    content  :: the rendered content from the template.
dmp_signal_post_render_template = Signal(providing_args=['request', 'context', 'template', 'content'])

#  Triggered when a RedirectException is encountered in the DMP controller.
#  This signal lets you adjust the values of the exception, such as where it is redirecting to.
#
#    request      :: the request object
#    exc          :: The exception object, including:
#                       exc.redirect_to (new url the router will process with)
#                       exc.permanent   (whether the browser should be told it is a permanent redirect or not)
dmp_signal_redirect_exception = Signal(providing_args=['request', 'exc'])

#  Triggered when an InternalRedirectException is encountered in the DMP controller.
#  This signal lets you adjust the values of the exception, such as where it is redirecting to.
#
#    request      :: the request object
#    exc          :: The exception object, including exc.redirect_to (new url the router will process with).
dmp_signal_internal_redirect_exception = Signal(providing_args=['request', 'exc'])
