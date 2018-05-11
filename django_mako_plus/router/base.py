####################################
###   The router base class

class Router(object):
    '''Common superclass of routers'''

    def get_response(self, request, *args, **kwargs):
        raise NotImplementedError()
