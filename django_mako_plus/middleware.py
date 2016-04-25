from django.core.exceptions import ImproperlyConfigured
from urllib.parse import unquote

from .util import URLParamList, get_dmp_app_configs, get_dmp_instance, DMP_OPTIONS


##########################################################
###   Middleware the prepares the request for
###   use with the controller.

class RequestInitMiddleware:
    '''Adds several fields to the request that our controller needs.

       This class MUST be included in settings.py -> MIDDLEWARE_CLASSES.
    '''
    def __init__(self):
        '''Constructor'''
        self.dmp_app_names = set(( config.name for config in get_dmp_app_configs() ))


    def process_request(self, request):
        '''Called for each browser request.  This adds the following fields to the request object:

           request.dmp_router_app       The Django application (such as "calculator").
           request.dmp_router_page      The view module (such as "calc" for calc.py).
           request.dmp_router_page_full The view module as specified in the URL, including the function name if specified.
           request.dmp_router_function  The function within the view module to be called (usually "process_request").
           request.dmp_router_module    The module path in Python terms, such as calculator.views.calc.
           request.urlparams            A list of the remaining url parts (see the calc.py example).

           This method is run as part of the middleware processing, so it runs long
           before the route_request() method at the top of this file.
        '''
        # split the path
        path_parts = request.path[1:].split('/') # [1:] to remove the leading /

        # splice the list if the settings need it
        start_index = DMP_OPTIONS.get('URL_START_INDEX', 0)
        if start_index > 0:
            path_parts = path_parts[start_index:]

        # ensure that we have at least 2 path_parts to work with
        # by adding the default app and/or page as needed
        if len(path_parts) == 0:
            path_parts.append(DMP_OPTIONS.get('DEFAULT_APP', 'homepage'))
            path_parts.append(DMP_OPTIONS.get('DEFAULT_PAGE', 'index'))

        elif len(path_parts) == 1: # /app or /page
            if path_parts[0] in self.dmp_app_names:  # one of our apps specified, so insert the default page
                path_parts.append(DMP_OPTIONS.get('DEFAULT_PAGE', 'index'))
            else:  # not one of our apps, so insert the app and assume path_parts[0] is a page in that app
                path_parts.insert(0, DMP_OPTIONS.get('DEFAULT_APP', 'homepage'))
                if not path_parts[1]: # was the page empty?
                    path_parts[1] = DMP_OPTIONS.get('DEFAULT_PAGE', 'index')

        else: # at this point in the elif, we know len(path_parts) >= 2
            if path_parts[0] not in self.dmp_app_names: # the first part was not one of our apps, so insert the default app
                path_parts.insert(0, DMP_OPTIONS.get('DEFAULT_APP', 'homepage'))
            if not path_parts[1]:  # is the page empty?
                path_parts[1] = DMP_OPTIONS.get('DEFAULT_PAGE', 'index')

        # set the app and page in the request
        request.dmp_router_app = path_parts[0]
        request.dmp_router_page = path_parts[1]
        request.dmp_router_page_full = path_parts[1]  # might be different from dmp_router_page when split by '.' below

        # see if a function is specified with the page (the . separates a function name)
        du_pos = request.dmp_router_page.find('.')
        if du_pos >= 0:
            request.dmp_router_function = request.dmp_router_page[du_pos+1:]
            request.dmp_router_function = request.dmp_router_function.replace('.', '_')  # python methods can't have dot, so replace with an underscore if in the name
            request.dmp_router_page = request.dmp_router_page[:du_pos]
        else:  # the . not found, and the __ not found, so go to default function name
            request.dmp_router_function = 'process_request'

        # set the class to be None (it is set later if we find a class-based view)
        request.dmp_router_class = None

        # set up the urlparams with the reamining path parts
        # note that I'm not using unquote_plus because the + switches to a space *after* the question mark (in the regular parameters)
        # in the normal url, spaces have to be quoted with %20.  Thanks Rosie for the tip.
        request.urlparams = URLParamList([ unquote(s) for s in path_parts[2:] ])
