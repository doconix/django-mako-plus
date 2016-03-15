#
#   Author:  Conan Albrecht <ca&byu,edu>
#   License: Apache Open Source License
#


# The version of DMP - used by sdist to publish to PyPI
__version__ = '3.0.7'

# pointer to our app config (Django looks for this exact variable name)
default_app_config = 'django_mako_plus.Config'

# our app config
from .apps import Config

# the exceptions
from .exceptions import InternalRedirectException
from .exceptions import RedirectException

# the router
from .router import view_function
from .router import route_request


# the middleware
from .middleware import RequestInitMiddleware


# the template engine
from .template import MakoTemplates
from .template import get_template_lookup
from .template import get_app_template_lookup
