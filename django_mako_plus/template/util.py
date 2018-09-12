from django.apps import apps
from django.utils.html import escape, mark_safe
from django.utils.encoding import force_text
from mako.exceptions import RichTraceback
from mako.template import Template
import mako.runtime

import io
import os, os.path


def template_inheritance(obj):
    '''
    Generator that iterates the template and its ancestors.
    The order is from most specialized (furthest descendant) to
    most general (furthest ancestor).

    `obj` can be either:
        1. Mako Template object
        2. Mako `self` object (available within a rendering template)
    '''
    if isinstance(obj, Template):
        obj = create_mako_context(obj)['self']
    elif isinstance(obj, mako.runtime.Context):
        obj = obj['self']
    while obj is not None:
        yield obj.template
        obj = obj.inherits


def create_mako_context(template_obj, **kwargs):
    # I'm hacking into private Mako methods here, but I can't see another
    # way to do this.  Hopefully this can be rectified at some point.
    kwargs.pop('self', None)  # some contexts have self in them, and it messes up render_unicode below because we get two selfs
    runtime_context = mako.runtime.Context(io.StringIO(), **kwargs)
    runtime_context._set_with_template(template_obj)
    _, mako_context = mako.runtime._populate_self_namespace(runtime_context, template_obj)
    return mako_context


def get_template_debug_info(error):
    '''
    Retrieves mako template information for Django's debug stack trace template.
    This allows Django to print Mako syntax/runtime template errors the same way
    it prints all other errors.
    '''
    from ..convenience import get_template_loader_for_path
    dmp = apps.get_app_config('django_mako_plus')
    loader = get_template_loader_for_path(os.path.join(dmp.path, 'templates'))
    # going straight to the mako template in case the error bubbles into our
    # adapter (which calls this function and would cause infinite loops)
    template = loader.get_mako_template('stack_trace.html')
    tback = RichTraceback(error, error.__traceback__)
    return {
        'message': '',
        'source_lines': [
            ( '', mark_safe(template.render_unicode(tback=tback)) ),
        ],
        'before': '',
        'during': '',
        'after': '',
        'top': 0,
        'bottom': 0,
        'total': 0,
        'line': tback.lineno or 0,
        'name': '',
        'start': 0,
        'end': 0,
    }
