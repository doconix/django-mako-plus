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


# the exceptions
from .exceptions import InternalRedirectException
from .exceptions import RedirectException


# the convenience functions
from .convenience import get_template_loader
from .convenience import get_template_loader_for_path


# the router
from .router import view_function
from .router import route_request


# the middleware
from .middleware import RequestInitMiddleware


# the template engine
from .engine import MakoTemplates


# the static files shortcuts
from .static_files import get_template_css
from .static_files import get_template_js
