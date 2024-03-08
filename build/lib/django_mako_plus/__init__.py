#
#   Author:  Conan Albrecht <ca&byu,edu>
#   License: Apache Open Source License
#


# pointer to our app config
# Django looks for this exact variable name


# the version
from .version import __version__


# the router, middleware, and view function decorator
from .middleware import RequestInitMiddleware
from .router import view_function, app_resolver, dmp_path


# converter decorator
from .converter import parameter_converter, ParameterConverter


# the middleware and template
# the template engine
from .engine import MakoTemplates


# the exceptions
from .exceptions import BaseRedirectException
from .exceptions import RedirectException
from .exceptions import PermanentRedirectException
from .exceptions import JavascriptRedirectException
from .exceptions import InternalRedirectException
from .exceptions import ConverterHttp404
from .exceptions import ConverterException


# filters and tags
from .filters import django_syntax, jinja2_syntax, alternate_syntax
from .templatetags.django_mako_plus import dmp_include

# used internally in compiled templates for autoescaping
# (needs to be exposed publicly so templates can see it)
from .template import ExpressionPostProcessor

# the http responses
from .http import HttpResponseJavascriptRedirect


# the convenience functions
#
# Instead of these functions, consider using request.dmp.render() and request.dmp.render_to_string(),
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
from .util import merge_dicts


# the urls
# I'm specifically not including urls.py here because I want it imported
# as late as possible (after all the apps are set up).  Django will import it
# when it processes the project's urls.py file.


# html content shortcuts
from .provider import links
from .provider import template_links, template_obj_links
# html content providers
from .provider.base import BaseProvider
from .provider.compile import CompileProvider, CompileScssProvider, CompileLessProvider
from .provider.context import JsContextProvider, jscontext
from .provider.link import LinkProvider, CssLinkProvider, JsLinkProvider
from .provider.webpack import WebpackJsLinkProvider
