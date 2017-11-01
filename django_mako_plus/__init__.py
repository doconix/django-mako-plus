#
#   Author:  Conan Albrecht <ca&byu,edu>
#   License: Apache Open Source License
#


# pointer to our app config
# Django looks for this exact variable name
default_app_config = 'django_mako_plus.Config'


# the version
from .version import __version__


# the app config
from .apps import Config


# the router and middleware
from .middleware import RequestInitMiddleware
from .router import route_request


# view_function decorator and converter classes
from .router import view_function
from .converter import DefaultConverter, set_default_converter, get_default_converter


# the middleware and template
# the template engine
from .engine import MakoTemplates


# the exceptions
from .exceptions import BaseRedirectException
from .exceptions import RedirectException
from .exceptions import PermanentRedirectException
from .exceptions import JavascriptRedirectException
from .exceptions import InternalRedirectException


# filters
from .filters import django_syntax, jinja2_syntax, alternate_syntax


# the http responses
from .http import HttpResponseJavascriptRedirect


# the convenience functions
#
# Instead of these functions, consider using request.dmp_render() and request.dmp_render_to_string(),
# which are monkey-patched onto every DMP-enabled app at load time.  See the documentation
# for information on why we do this.
#
from .convenience import render_template
from .convenience import render_template_for_path
from .convenience import get_template
from .convenience import get_template_for_path
from .convenience import get_template_loader
from .convenience import get_template_loader_for_path


# the utilities
from .util import get_dmp_instance
from .util import get_dmp_app_configs


# the urls
# I'm specifically not including urls.py here because I want it imported
# as late as possible (after all the apps are set up).  Django will import it
# when it processes the project's urls.py file.


# html content shortcuts
from .provider import links
from .provider import template_links
# html content providers
from .provider import BaseProvider
from .provider import LinkProvider, CssLinkProvider, JsLinkProvider, jscontext
from .provider import CompileProvider, CompileScssProvider, CompileLessProvider
# html content providers (deprecated)
from .provider import MakoCssProvider, MakoJsProvider
from .provider import link_css, link_js, link_template_css, link_template_js
