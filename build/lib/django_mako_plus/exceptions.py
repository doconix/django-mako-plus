from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect

from .http import HttpResponseJavascriptRedirect, REDIRECT_HEADER_KEY


###############################################################
###   Exceptions used to direct the controller


class BaseRedirectException(Exception):
    '''
    Superclass of DMP redirect exceptions
    '''


class InternalRedirectException(BaseRedirectException):
    '''
    View functions can throw this exception to indicate that a new view
    should be called by the HtmlPageServer.  The current view function
    will end immediately, and processing will be passed to the new view function.
    '''
    def __init__(self, redirect_module, redirect_function):
        '''
        Indicates the new view to be called.  The view should be given relative to the project root.
        The parameters should be strings, not the actual module or function reference.
        '''
        super(InternalRedirectException, self).__init__()
        self.redirect_module = redirect_module
        self.redirect_function = redirect_function


class RedirectException(BaseRedirectException):
    '''
    Immediately stops processing of a view function or template and redirects to the given page
    using the standard 302 response status header.

    After the redirect_to parameter, you can use any of the normal HttpResponse constructor arguments.

    A custom header is set in the response.  This allows middleware, your web server, or
    calling JS code to adjust the redirect if needed.
    '''
    def __init__(self, redirect_to, *args, **kwargs):
        self.redirect_to = redirect_to
        self.args = args
        self.kwargs = kwargs

    def get_response(self, request, *args, **kwargs):
        '''Returns the redirect response for this exception.'''
        # normal process
        response = HttpResponseRedirect(self.redirect_to)
        response[REDIRECT_HEADER_KEY] = self.redirect_to
        return response


class PermanentRedirectException(RedirectException):
    '''
    Immediately stops processing of a view function or template and redirects to the given page
    using the standard 301 response status header.

    After the redirect_to parameter, you can use any of the normal HttpResponse constructor arguments.

    A custom header is set in the response.  This allows middleware, your web server, or
    calling JS code to adjust the redirect if needed.

    '''
    def get_response(self, request):
        '''Returns the redirect response for this exception.'''
        response = HttpResponsePermanentRedirect(self.redirect_to, *self.args, **self.kwargs)
        response[REDIRECT_HEADER_KEY] = self.redirect_to
        return response


class JavascriptRedirectException(RedirectException):
    '''
    Immediately stops processing of a view function or template and redirects to the given page.

    Sends a regular HTTP 200 OK response that contains Javascript to
    redirect the browser:

        <script>window.location.href="...";</script>.

    If redirect_to is empty, it redirects to the current location (essentially refreshing
    the current page):

        <script>window.location.href=window.location.href;</script>.

    Normally, redirecting should be done via HTTP 302 rather than Javascript.
    Use this class when your only choice is through Javascript.

    For example, suppose you need to redirect the top-level page from an Ajax response.
    Ajax redirects normally only redirects the Ajax itself (not the page that initiated the call),
    and this default behavior is usually what is needed.  However, there are instances when the
    entire page must be redirected, even if the call is Ajax-based.

    After the redirect_to parameter, you can use any of the normal HttpResponse constructor arguments.

    If you need to omit the surrounding <script> tags, send "include_script_tag=False" to
    the constructor. One use case for omitting the tags is when the caller is a
    JQuery $.script() ajax call.

    A custom header is set in the response.  This allows middleware, your web server, or
    calling JS code to adjust the redirect if needed.

    Note that this method doesn't use the <meta> tag or Refresh header method because
    they aren't predictable within Ajax (for example, JQuery seems to ignore them).
    '''
    def get_response(self, request):
        '''Returns the redirect response for this exception.'''
        # the redirect key is already placed in the response by HttpResponseJavascriptRedirect
        return HttpResponseJavascriptRedirect(self.redirect_to, *self.args, **self.kwargs)




################################################################
###   Other exceptions not exposed beyond DMP

class SassCompileException(Exception):
    '''
    DEPRECATED.  This will be removed at some point.

    Raised when a .scss file won't compile
    '''
    def __init__(self, cmd, message):
        self.cmd = cmd
        self.message = message

    def __str__(self):
        return self.message


