from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist, TemplateSyntaxError, Context, RequestContext

from mako.exceptions import TopLevelLookupException, TemplateLookupException, CompileException, SyntaxException, html_error_template
from mako.lookup import TemplateLookup
from mako.template import Template

from .exceptions import InternalRedirectException, RedirectException
from .signals import dmp_signal_pre_render_template, dmp_signal_post_render_template, dmp_signal_redirect_exception
from .util import get_dmp_instance, log, DMP_OPTIONS

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
        if not os.path.isdir(template_dir):
            raise ImproperlyConfigured('Cannot create template loader because its directory does not exist: %s' % template_dir)

        # calculate the cache root and template search directories
        self.cache_root = os.path.join(template_dir, DMP_OPTIONS.get('TEMPLATES_CACHE_DIR', '.cached_templates'))
        self.template_search_dirs = [ template_dir ]
        if DMP_OPTIONS.get('TEMPLATES_DIRS'):
            self.template_search_dirs.extend(DMP_OPTIONS.get('TEMPLATES_DIRS'))
        # include the project base directory so template inheritance can cross apps by starting with /
        self.template_search_dirs.append(settings.BASE_DIR)

        # create the actual Mako TemplateLookup, which does the actual work
        self.tlookup = TemplateLookup(directories=self.template_search_dirs, imports=DMP_OPTIONS.get('DEFAULT_TEMPLATE_IMPORTS'), module_directory=self.cache_root, collection_size=2000, filesystem_checks=settings.DEBUG, input_encoding=DMP_OPTIONS.get('DEFAULT_TEMPLATE_ENCODING', 'utf-8'))


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
            log.error('template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
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
        '''Renders a template using the Mako system.  This method signature conforms to
           the Django template API, which specifies that template.render() returns a string.

           The method triggers two signals:
             1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
                the normal template object that is used for the render operation.
             2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
                template object render.

           @context  A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                     or a Django Context object.
           @request  The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                     file will be ignored but the template will otherwise render fine.
           @def_name Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                     If the section is a <%def>, it must have no parameters.  For example, def_name="foo" will call
                     <%block name="foo"></%block> or <%def name="foo()"></def> within the template.  This is an
                     extension to the Django API, so it is optional.

           The rendered string is returned.
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
            log.debug('Rendering template %s' % (self.mako_template.filename or 'string'))
        if settings.DEBUG:
            try:
                content = render_obj.render_unicode(**context_dict)
            except:
                log.exception('Exception raised during template rendering:')  # to the console
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


    def render_to_response(self, context=None, request=None, def_name=None):
        '''Renders the template and returns an HttpRequest object containing its content.

           This method returns a django.http.Http404 exception if the template is not found.
           If the template raises a django_mako_plus.RedirectException, the browser is redirected to
             the given page, and a new request from the browser restarts the entire DMP routing process.
           If the template raises a django_mako_plus.InternalRedirectException, the entire DMP
             routing process is restarted internally (the browser doesn't see the redirect).

           The method triggers two signals:
             1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
                the normal template object that is used for the render operation.
             2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
                template object render.

           @request  The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                     file will be ignored but the template will otherwise render fine.
           @template The template file path to render.  This is relative to the app_path/controller_TEMPLATES_DIR/ directory.
                     For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                     set up the variables as described in the documentation above.
           @context  A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                     or a Django Context object.
           @def_name Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                     If the section is a <%def>, it must have no parameters.  For example, def_name="foo" will call
                     <%block name="foo"></%block> or <%def name="foo()"></def> within the template.
        '''
        try:
            content_type = mimetypes.types_map.get(os.path.splitext(self.mako_template.filename)[1].lower(), 'text/html')
            content = self.render(context=context, request=request, def_name=def_name)
            return HttpResponse(content.encode(settings.DEFAULT_CHARSET), content_type='%s; charset=%s' % (content_type, settings.DEFAULT_CHARSET))
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
