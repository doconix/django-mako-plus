from django.http import HttpResponse

# this redirect key is (hopefully) unique but generic so it doesn't signpost the use of DMP/Django.
# not prefixing with X- because that's now deprecated.
REDIRECT_HEADER_KEY = 'Redirect-Location'


###############################################################################
###   Redirect with Javascript instead of 301/302
###   See also exceptions.py for two additional redirect methods

class HttpResponseJavascriptRedirect(HttpResponse):
    '''
    Sends a regular HTTP 200 OK response that contains Javascript to
    redirect the browser:

        <script>window.location.assign("...");</script>.

    If redirect_to is empty, it redirects to the current location (essentially refreshing
    the current page):

        <script>window.location.assign(window.location.href);</script>.

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
    def __init__(self, redirect_to=None, *args, **kwargs):
        # set up the code
        if redirect_to:
            script = 'window.location.assign("{}");'.format(redirect_to.split('#')[0])
        else:
            script = 'window.location.assign(window.location.href.split("#")[0])'
        # do we need to add the <script> tag? (that's the default)
        if kwargs.pop('include_script_tag', True):
            script = '<script>{}</script>'.format(script)
        # call the super
        super().__init__(script, *args, **kwargs)
        # add the custom header
        self[REDIRECT_HEADER_KEY] = redirect_to or 'window.location.href'
