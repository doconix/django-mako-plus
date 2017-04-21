from django.conf import settings
from django_mako_plus import view_function

from .. import dmp_render, dmp_render_to_string

import datetime


@view_function
def process_request(request):
    return dmp_render(request, 'index.html', {
        'current_time': datetime.datetime.now(),
    })
