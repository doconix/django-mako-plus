from django.apps import apps
from django.conf import settings
from django.http import HttpResponse
from django.utils.html import mark_safe
from django.template import Context, RequestContext

from ..exceptions import RedirectException
from ..signals import dmp_signal_pre_render_template, dmp_signal_post_render_template, dmp_signal_redirect_exception
from ..util import log
from .util import get_template_debug

import logging
import mimetypes
import os
import os.path
import sys



class MakoTemplateAdapter(object):
    '''A thin wrapper for a Mako template object that provides the Django API methods.'''
    def __init__(self, mako_template, def_name=None):
        '''
        Creates an adapter that corresponds to the Django API.

        If def_name is provided, template rendering will be limited to the named def/block (see Mako docs).
        This can also be provided in the call to render().
        '''
        self.mako_template = mako_template
        self.def_name = def_name

    @property
    def engine(self):
        '''Returns the DMP engine (method required by Django specs)'''
        dmp = apps.get_app_config('django_mako_plus')
        return dmp.engine

    @property
    def name(self):
        '''Returns the name of this template (if created from a file) or "string" if not'''
        if self.mako_template.filename:
            return os.path.basename(self.mako_template.filename)
        return 'string'

    def has_def(self, name):
        '''Convenience passthrough to the Mako template'''
        return self.mako_template.has_def(name)

    def get_def(self, name):
        '''Convenience passthrough to the Mako template'''
        return self.mako_template.get_def(name)

    def list_defs(self):
        '''Convenience passthrough to the Mako template'''
        return self.mako_template.list_defs()

    def render(self, context=None, request=None, def_name=None):
        '''
        Renders a template using the Mako system.  This method signature conforms to
        the Django template API, which specifies that template.render() returns a string.

            @context  A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                      or a Django Context object.
            @request  The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                      file will be ignored but the template will otherwise render fine.
            @def_name Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                      If the section is a <%def>, any parameters must be in the context dictionary.  For example,
                      def_name="foo" will call <%block name="foo"></%block> or <%def name="foo()"></def> within
                      the template.

        Returns the rendered template as a unicode string.

        The method triggers two signals:
            1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
               the normal template object that is used for the render operation.
            2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
               template object render.
        '''
        dmp = apps.get_app_config('django_mako_plus')
        # set up the context dictionary, which is the variables available throughout the template
        context_dict = {}
        # if request is None, add some default items because the context processors won't happen
        if request is None:
            context_dict['settings'] = settings
            context_dict['STATIC_URL'] = settings.STATIC_URL
        # let the context_processors add variables to the context.
        if not isinstance(context, Context):
            context = Context(context) if request is None else RequestContext(request, context)
        with context.bind_template(self):
            for d in context:
                context_dict.update(d)
        context_dict.pop('self', None)  # some contexts have self in them, and it messes up render_unicode below because we get two selfs

        # send the pre-render signal
        if dmp.options['SIGNALS'] and request is not None:
            for receiver, ret_template_obj in dmp_signal_pre_render_template.send(sender=self, request=request, context=context, template=self.mako_template):
                if ret_template_obj is not None:
                    if isinstance(ret_template_obj, MakoTemplateAdapter):
                        self.mako_template = ret_template_obj.mako_template   # if the signal function sends a MakoTemplateAdapter back, use the real mako template inside of it
                    else:
                        self.mako_template = ret_template_obj                 # if something else, we assume it is a mako.template.Template, so use it as the template

        # do we need to limit down to a specific def?
        # this only finds within the exact template (won't go up the inheritance tree)
        render_obj = self.mako_template
        if def_name is None:
            def_name = self.def_name
        if def_name:  # do we need to limit to just a def?
            render_obj = self.mako_template.get_def(def_name)

        # PRIMARY FUNCTION: render the template
        if log.isEnabledFor(logging.INFO):
            log.info('rendering template %s%s%s', self.name, ('::' if def_name else ''), def_name or '')
        if settings.DEBUG:
            try:
                content = render_obj.render_unicode(**context_dict)
            except Exception as e:
                log.exception('exception raised during template rendering: %s', e)  # to the console
                e.template_debug = get_template_debug('%s%s%s' % (self.name, ('::' if def_name else ''), def_name or ''), e)
                raise
        else:  # this is outside the above "try" loop because in non-DEBUG mode, we want to let the exception throw out of here (without having to re-raise it)
            content = render_obj.render_unicode(**context_dict)

        # send the post-render signal
        if dmp.options['SIGNALS'] and request is not None:
            for receiver, ret_content in dmp_signal_post_render_template.send(sender=self, request=request, context=context, template=self.mako_template, content=content):
                if ret_content is not None:
                    content = ret_content  # sets it to the last non-None return in the signal receiver chain

        # return
        return mark_safe(content)


    def render_to_response(self, context=None, request=None, def_name=None, content_type=None, status=None, charset=None):
        '''
        Renders the template and returns an HttpRequest object containing its content.

        This method returns a django.http.Http404 exception if the template is not found.
        If the template raises a django_mako_plus.RedirectException, the browser is redirected to
        the given page, and a new request from the browser restarts the entire DMP routing process.
        If the template raises a django_mako_plus.InternalRedirectException, the entire DMP
        routing process is restarted internally (the browser doesn't see the redirect).

            @request      The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                          file will be ignored but the template will otherwise render fine.
            @template     The template file path to render.  This is relative to the app_path/controller_TEMPLATES_DIR/ directory.
                          For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                          set up the variables as described in the documentation above.
            @context      A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                          or a Django Context object.
            @def_name     Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                          For example, def_name="foo" will call <%block name="foo"></%block> or <%def name="foo()"></def> within the template.
            @content_type The MIME type of the response.  Defaults to settings.DEFAULT_CONTENT_TYPE (usually 'text/html').
            @status       The HTTP response status code.  Defaults to 200 (OK).
            @charset      The charset to encode the processed template string (the output) with.  Defaults to settings.DEFAULT_CHARSET (usually 'utf-8').

        The method triggers two signals:
            1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
               the normal template object that is used for the render operation.
            2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
               template object render.
        '''
        try:
            if content_type is None:
                content_type = mimetypes.types_map.get(os.path.splitext(self.mako_template.filename)[1].lower(), settings.DEFAULT_CONTENT_TYPE)
            if charset is None:
                charset = settings.DEFAULT_CHARSET
            if status is None:
                status = 200
            content = self.render(context=context, request=request, def_name=def_name)
            return HttpResponse(content.encode(charset), content_type='%s; charset=%s' % (content_type, charset), status=status)

        except RedirectException: # redirect to another page
            e = sys.exc_info()[1]
            if request is None:
                log.info('a template redirected processing to %s', e.redirect_to)
            else:
                log.info('view function %s.%s redirected processing to %s', request.dmp.module, request.dmp.function, e.redirect_to)
            # send the signal
            dmp = apps.get_app_config('django_mako_plus')
            if dmp.options['SIGNALS']:
                dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
            # send the browser the redirect command
            return e.get_response(request)
