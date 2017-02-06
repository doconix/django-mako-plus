from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.template import TemplateDoesNotExist, TemplateSyntaxError, Context, RequestContext

from mako.exceptions import TopLevelLookupException, TemplateLookupException, CompileException, SyntaxException, html_error_template
from mako.lookup import TemplateLookup
from mako.template import Template

from .convenience import get_template as convenience_get_template
from .exceptions import InternalRedirectException, RedirectException
from .signals import dmp_signal_pre_render_template, dmp_signal_post_render_template, dmp_signal_redirect_exception
from .util import get_dmp_instance, log, DMP_OPTIONS
from .util import DMP_VIEW_TEMPLATE

import os, os.path, sys, mimetypes, logging



##############################################################
###   Looks up Mako templates

class MakoTemplateLoader:
    '''Renders Mako templates.'''
    def __init__(self, app_path, template_subdir='templates'):
        '''
        Creates a renderer to the given template_subdir in app_path.

        The loader looks in the app_path/templates directory unless
        the template_subdir parameter overrides this default.

        You should not normally create this object because it bypasses
        the DMP cache.  Instead, call get_template_loader() or
        get_template_loader_for_path().
        '''
        # calculate the template directory and check that it exists
        if template_subdir == None:  # None skips adding the template_subdir
            template_dir = os.path.abspath(app_path)
        else:
            template_dir = os.path.abspath(os.path.join(app_path, template_subdir))
        # I used to check for the existence of the template dir here, but it caused error
        # checking at engine load time (too soon).  I now wait until get_template() is called,
        # which fails with a TemplateDoesNotExist exception if the template_dir doesn't exist.

        # calculate the cache root and template search directories
        self.cache_root = os.path.join(template_dir, DMP_OPTIONS.get('TEMPLATES_CACHE_DIR', '.cached_templates'))
        self.template_search_dirs = [ template_dir ]
        if DMP_OPTIONS.get('TEMPLATES_DIRS'):
            self.template_search_dirs.extend(DMP_OPTIONS.get('TEMPLATES_DIRS'))
        # Mako doesn't allow parent directory inheritance, such as <%inherit file="../../otherapp/templates/base.html"/>
        # including the project base directory allows this through "absolute" like <%inherit file="/otherapp/templates/base.html"/>
        # (note the leading slash, which means BASE_DIR)
        self.template_search_dirs.append(settings.BASE_DIR)

        # create the actual Mako TemplateLookup, which does the actual work
        self.tlookup = TemplateLookup(directories=self.template_search_dirs, imports=DMP_OPTIONS['DEFAULT_TEMPLATE_IMPORTS'], module_directory=self.cache_root, collection_size=2000, filesystem_checks=settings.DEBUG, input_encoding=DMP_OPTIONS.get('DEFAULT_TEMPLATE_ENCODING', 'utf-8'))


    def get_template(self, template):
        '''Retrieve a *Django* API template object for the given template name, using the app_path and template_subdir
           settings in this object.  This method still uses the corresponding Mako template and engine, but it
           gives a Django API wrapper around it so you can use it the same as any Django template.

           This method corresponds to the Django templating system API.
           This method raises a Django exception if the template is not found or cannot compile.
        '''
        try:
            # wrap the mako template in an adapter that gives the Django template API
            return MakoTemplateAdapter(self.get_mako_template(template))
        except (TopLevelLookupException, TemplateLookupException) as e: # Mako exception raised
            log.error('template "%s" not found in search path: %s' % (template, self.template_search_dirs))
            raise TemplateDoesNotExist('Template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
        except (CompileException, SyntaxException) as e: # Mako exception raised
            log.error('template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
            raise TemplateSyntaxError('Template "%s" raised an error: %s' % (template, e))


    def get_mako_template(self, template):
        '''Retrieve the real *Mako* template object for the given template name without any wrapper,
           using the app_path and template_subdir settings in this object.

           This method is an alternative to get_template().  Use it when you need the actual Mako template object.
           This method raises a Mako exception if the template is not found or cannot compile.
        '''
        # get the template
        template_obj = self.tlookup.get_template(template)

        # if this is the first time the template has been pulled from self.tlookup, add a few extra attributes
        if not hasattr(template_obj, 'template_path'):
            template_obj.template_path = template
        if not hasattr(template_obj, 'template_full_path'):
            template_obj.template_full_path = template_obj.filename

        # get the template
        return template_obj




class MakoTemplateAdapter(object):
    '''A thin wrapper for a Mako template object that provides the Django API methods.'''
    def __init__(self, mako_template):
        self.mako_template = mako_template


    @property
    def engine(self):
        '''Returns the DMP engine (method required by Django specs)'''
        return get_dmp_instance()


    def render(self, context=None, request=None, def_name=None):
        '''
        Renders a template using the Mako system.  This method signature conforms to
        the Django template API, which specifies that template.render() returns a string.

            @context  A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                      or a Django Context object.
            @request  The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                      file will be ignored but the template will otherwise render fine.
            @def_name Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                      If the section is a <%def>, it must have no parameters.  For example, def_name="foo" will call
                      <%block name="foo"></%block> or <%def name="foo()"></def> within the template.  This is an
                      extension to the Django API, so it is optional.

        Returns the rendered template as a unicode string.

        The method triggers two signals:
            1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
               the normal template object that is used for the render operation.
            2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
               template object render.
        '''
        # set up the context dictionary, which is the variables available throughout the template
        context_dict = {}
        # if request is None, add some default items because the context processors won't happen
        if request == None:
            context_dict['settings'] = settings
            context_dict['STATIC_URL'] = settings.STATIC_URL
        # let the context_processors add variables to the context.
        if not isinstance(context, Context):
            context = Context(context) if request == None else RequestContext(request, context)
        with context.bind_template(self):
            for d in context:
                context_dict.update(d)
        # some contexts have self in them, and it messes up render_unicode below because we get two selfs
        context_dict.pop('self', None)

        # send the pre-render signal
        if DMP_OPTIONS.get('SIGNALS', False) and request != None:
            for receiver, ret_template_obj in dmp_signal_pre_render_template.send(sender=self, request=request, context=context, template=self.mako_template):
                if ret_template_obj != None:
                    if isinstance(ret_template_obj, MakoTemplateAdapter):
                        self.mako_template = ret_template_obj.mako_template   # if the signal function sends a MakoTemplateAdapter back, use the real mako template inside of it
                    else:
                        self.mako_template = ret_template_obj                 # if something else, we assume it is a mako.template.Template, so use it as the template

        # do we need to limit down to a specific def?
        # this only finds within the exact template (won't go up the inheritance tree)
        # I wish I could make it do so, but can't figure this out
        render_obj = self.mako_template
        if def_name:  # do we need to limit to just a def?
            render_obj = self.mako_template.get_def(def_name)

        # PRIMARY FUNCTION: render the template
        if log.isEnabledFor(logging.DEBUG):
            template_debug_name = self.mako_template.filename or 'string'
            if def_name:
                template_debug_name = '%s -> %s' % (template_debug_name, def_name)
            log.debug('rendering template %s' % template_debug_name)
        if settings.DEBUG:
            try:
                content = render_obj.render_unicode(**context_dict)
            except:
                log.exception('exception raised during template rendering:')  # to the console
                content = html_error_template().render_unicode()       # to the browser
        else:  # this is outside the above "try" loop because in non-DEBUG mode, we want to let the exception throw out of here (without having to re-raise it)
            content = render_obj.render_unicode(**context_dict)

        # send the post-render signal
        if DMP_OPTIONS.get('SIGNALS', False) and request != None:
            for receiver, ret_content in dmp_signal_post_render_template.send(sender=self, request=request, context=context, template=self.mako_template, content=content):
                if ret_content != None:
                    content = ret_content  # sets it to the last non-None return in the signal receiver chain

        # return
        return content


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
            if request == None:
                log.info('a template redirected processing to %s' % (request.dmp_router_module, request.dmp_router_function, e.redirect_to))
            else:
                log.info('view function %s.%s redirected processing to %s' % (request.dmp_router_module, request.dmp_router_function, e.redirect_to))
            # send the signal
            if DMP_OPTIONS.get('SIGNALS', False):
                dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
            # send the browser the redirect command
            return e.get_response(request)







#############################################################
###   Helper function that calls render_to_response()
###   for a template.  This makes it look like a view
###   function.
###

class TemplateViewFunction(object):
    '''
    This is used in engine.get_view_function to make a MakoTemplateAdapter
    object look like a view function.
    '''
    _dmp_view_type = DMP_VIEW_TEMPLATE

    def __init__(self, app_name, template_name):
        # we don't keep the actual template objects because we need to get from the loader each time (so Mako can check for updates, etc.)
        self.app_name = app_name
        self.template_name = template_name

    def get_template(self):
        # this is split into a separate method because engine.get_view_function() verifies the existance of the template
        # raises a TemplateDoesNotExist if not found
        return convenience_get_template(self.app_name, self.template_name)


    def __call__(self, request, *args, **kwargs):
        # called from the router to process a request
        return self.get_template().render_to_response(request=request, context=kwargs)
