from django.conf import settings
from django.http import HttpResponse
from django.template import TemplateDoesNotExist, TemplateSyntaxError, Context, RequestContext

from mako.exceptions import TopLevelLookupException, TemplateLookupException, CompileException, SyntaxException, html_error_template
from mako.lookup import TemplateLookup
from mako.template import Template

from .exceptions import RedirectException
from .signals import dmp_signal_pre_render_template, dmp_signal_post_render_template, dmp_signal_redirect_exception
from .util import get_dmp_instance, log, DMP_OPTIONS

import os, os.path, sys, mimetypes, logging, warnings



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
        if template_subdir is None:  # None skips adding the template_subdir
            self.template_dir = os.path.abspath(app_path)
        else:
            self.template_dir = os.path.abspath(os.path.join(app_path, template_subdir))
        # I used to check for the existence of the template dir here, but it caused error
        # checking at engine load time (too soon).  I now wait until get_template() is called,
        # which fails with a TemplateDoesNotExist exception if the template_dir doesn't exist.

        # calculate the cache root and template search directories
        self.cache_root = os.path.join(self.template_dir, DMP_OPTIONS.get('TEMPLATES_CACHE_DIR', '.cached_templates'))
        self.template_search_dirs = [ self.template_dir ]
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
            raise TemplateDoesNotExist('Template "%s" not found in search path: %s.' % (template, self.template_search_dirs))
        except (CompileException, SyntaxException) as e: # Mako exception raised
            raise TemplateSyntaxError('Template "%s" raised an error: %s' % (template, e))


    def get_mako_template(self, template, force=False):
        '''Retrieve the real *Mako* template object for the given template name without any wrapper,
           using the app_path and template_subdir settings in this object.

           This method is an alternative to get_template().  Use it when you need the actual Mako template object.
           This method raises a Mako exception if the template is not found or cannot compile.
        
           If force is True, an empty Mako template will be created when the file does not exist.
           This option is used by the providers part of DMP and normally be left False.
        '''
        if template is None:
            raise TemplateLookupException('Template "%s" not found in search path: %s.' % (template, self.template_search_dirs))

        # get the template
        try:
            template_obj = self.tlookup.get_template(template)
        except TemplateLookupException:
            if not force:
                raise
            template_obj = Template('', filename=os.path.join(self.template_dir, template))

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
                      If the section is a <%def>, any parameters must be in the context dictionary.  For example,
                      def_name="foo" will call <%block name="foo"></%block> or <%def name="foo()"></def> within
                      the template.  This is an extension to the Django API, so it is optional.

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
        if DMP_OPTIONS.get('SIGNALS', False) and request is not None:
            for receiver, ret_template_obj in dmp_signal_pre_render_template.send(sender=self, request=request, context=context, template=self.mako_template):
                if ret_template_obj is not None:
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
        template_name = '%s::%s' % (self.mako_template.filename or 'string', def_name or 'body')
        if log.isEnabledFor(logging.DEBUG):
            log.debug('rendering template %s', template_name)
        if settings.DEBUG:
            try:
                content = render_obj.render_unicode(**context_dict)
            except Exception as e:
                log.exception('exception raised during template rendering: %s', e)  # to the console
                content = html_error_template().render_unicode()       # to the browser
        else:  # this is outside the above "try" loop because in non-DEBUG mode, we want to let the exception throw out of here (without having to re-raise it)
            content = render_obj.render_unicode(**context_dict)
            
        # send the post-render signal
        if DMP_OPTIONS.get('SIGNALS', False) and request is not None:
            for receiver, ret_content in dmp_signal_post_render_template.send(sender=self, request=request, context=context, template=self.mako_template, content=content):
                if ret_content is not None:
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
            if request is None:
                log.info('a template redirected processing to %s', request.dmp_router_module, request.dmp_router_function, e.redirect_to)
            else:
                log.info('view function %s.%s redirected processing to %s', request.dmp_router_module, request.dmp_router_function, e.redirect_to)
            # send the signal
            if DMP_OPTIONS.get('SIGNALS', False):
                dmp_signal_redirect_exception.send(sender=sys.modules[__name__], request=request, exc=e)
            # send the browser the redirect command
            return e.get_response(request)



#################################################################################
###
###  The middleware places these on the request object during process_view():
###
###     request.render(...) 
###     request.render_to_string(...)
###

def render_to_string_shortcut(app_name, request):
    # I'm doing this inner function for late lookups (get_template_loader), just in case new template loader objects are added after creation.
    def wrapper(template, context=None, def_name=None, subdir='templates'):
        '''
        A shortcut to render a template.  This is one of the most-used functions in the DMP framework.
        This method is added to the the request object during middleware's process_view phase.

            @template     The template file path to render.  This is relative to the app_path/controller_TEMPLATES_DIR/ directory.
                          For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                          set up the variables as described in the documentation above.
            @context      A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                          or a Django Context object.
            @def_name     Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                          For example, def_name="foo" will call <%block name="foo"></%block> or <%def name="foo()"></def> within the template.
            @subdir       The sub-folder within the app where the template resides.  Templates are normally placed
                          in project/appname/templates/, which is the default value.

        Returns the rendered template as a unicode string.

        Examples of use from within appname/views/someview.py:

            from django_mako_plus import view_function

            @view_function
            def process_request(request):
                # render an HTML template in appname/templates/sometemplate.html to a string
                html = request.dmp_render_to_string('sometemplate.html', { 'var1': 'value' })
                # (do something with the html)

            @view_function
            def another_func(request):
                # render some dynamic JS in appname/scripts/sometemplate.js (which has embedded Mako code)
                html = request.dmp_render_to_string('sometemplate.js', { 'var1': 'value' }, subdir="scripts")
                # (do something with the html)

            @view_function
            def yet_another(request):
                # render a single <block name="toolbar"> instead of the entire template in appname/templates/sometemplate.html to a string
                html = request.dmp_render_to_string('sometemplate.html', { 'var1': 'value' }, def_name='toolbar')
                # (do something with the html)

        The method triggers two signals:
            1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
               the normal template object that is used for the render operation.
            2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
               template object render.
        '''
        template_loader = get_dmp_instance().get_template_loader(app_name, subdir)
        template_adapter = template_loader.get_template(template)
        return getattr(template_adapter, 'render')(context=context, request=request, def_name=def_name)

    # outer function return
    return wrapper


def render_to_response_shortcut(app_name, request):
    # I'm doing this inner function for late lookups (get_template_loader), just in case new template loader objects are added after creation.
    def wrapper(template, context=None, def_name=None, subdir='templates', content_type=None, status=None, charset=None):
        '''
        A shortcut to render a template.  This is one of the most-used functions in the DMP framework.
        This method is added to the the request object during middleware's process_view phase.

            @template     The template file path to render.  This is relative to the app_path/controller_TEMPLATES_DIR/ directory.
                          For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                          set up the variables as described in the documentation above.
            @context      A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                          or a Django Context object.
            @def_name     Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                          For example, def_name="foo" will call <%block name="foo"></%block> or <%def name="foo()"></def> within the template.
            @subdir       The sub-folder within the app where the template resides.  Templates are normally placed
                          in project/appname/templates/, which is the default value.
            @content_type The MIME type of the response.  Defaults to settings.DEFAULT_CONTENT_TYPE (usually 'text/html').
            @status       The HTTP response status code.  Defaults to 200 (OK).
            @charset      The charset to encode the processed template string (the output) with.  Defaults to settings.DEFAULT_CHARSET (usually 'utf-8').

        Returns a Django HttpResponse containing the rendered template.

        Examples of use from within appname/views/someview.py:

            from django_mako_plus import view_function

            @view_function
            def process_request(request):
                # return an HTML template in appname/templates/sometemplate.html
                return request.dmp_render('sometemplate.html', { 'var1': 'value' })

            @view_function
            def another_func(request):
                # return some dynamic JS in appname/scripts/sometemplate.js (which has embedded Mako code)
                return request.dmp_render('sometemplate.js', { 'var1': 'value' }, subdir="scripts")

            @view_function
            def yet_another(request):
                # return a single <block name="toolbar"> instead of the entire template in appname/templates/sometemplate.html
                return request.dmp_render('sometemplate.html', { 'var1': 'value' }, def_name='toolbar')

        The method triggers two signals:
            1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
               the normal template object that is used for the render operation.
            2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
               template object render.
        '''
        template_loader = get_dmp_instance().get_template_loader(app_name, subdir)
        template_adapter = template_loader.get_template(template)
        return getattr(template_adapter, 'render_to_response')(context=context, request=request, def_name=def_name, content_type=content_type, status=status, charset=charset)

    # outer function return
    return wrapper



############################################################################
###
###  DEPRECATED VERSIONS
###  (these attach to the app-level module, but phasing them out)
###
###  Monkey-patch functions to enable render() and render_to_string()
###  within the app scope of *each* DMP-enabled app.
###

def render_to_string_shortcut_deprecated(app_name):
    # I'm doing this inner function for late lookups (get_template_loader), just in case new template loader objects are added after creation.
    def wrapper(request, template, context=None, def_name=None, subdir='templates'):
        '''
        A shortcut to render a template.  This is one of the primary functions in the DMP framework.
        This method is added to the app space of each DMP-enabled app at load time.

            @request      The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                          file will be ignored but the template will otherwise render fine.
            @template     The template file path to render.  This is relative to the app_path/controller_TEMPLATES_DIR/ directory.
                          For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                          set up the variables as described in the documentation above.
            @context      A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                          or a Django Context object.
            @def_name     Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                          For example, def_name="foo" will call <%block name="foo"></%block> or <%def name="foo()"></def> within the template.
            @subdir       The sub-folder within the app where the template resides.  Templates are normally placed
                          in project/appname/templates/, which is the default value.

        Returns the rendered template as a unicode string.

        Examples of use from within appname/views/someview.py:

            from django_mako_plus import view_function

            @view_function
            def process_request(request):
                # render an HTML template in appname/templates/sometemplate.html to a string
                html = render_to_string(request, 'sometemplate.html', { 'var1': 'value' })
                # (do something with the html)

            @view_function
            def another_func(request):
                # render some dynamic JS in appname/scripts/sometemplate.js (which has embedded Mako code)
                html = render_to_string(request, 'sometemplate.js', { 'var1': 'value' }, subdir="scripts")
                # (do something with the html)

            @view_function
            def yet_another(request):
                # render a single <block name="toolbar"> instead of the entire template in appname/templates/sometemplate.html to a string
                html = render_to_string(request, 'sometemplate.html', { 'var1': 'value' }, def_name='toolbar')
                # (do something with the html)

        The method triggers two signals:
            1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
               the normal template object that is used for the render operation.
            2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
               template object render.
        '''
        template_loader = get_dmp_instance().get_template_loader(app_name, subdir)
        template_adapter = template_loader.get_template(template)
        warnings.warn('As of DMP 4.2, `dmp_render` has changed to `request.dmp_render`. Please see the documentation for more information.', DeprecationWarning)
        return getattr(template_adapter, 'render')(context=context, request=request, def_name=def_name)

    # outer function return
    return wrapper


def render_to_response_shortcut_deprecated(app_name):
    # I'm doing this inner function for late lookups (get_template_loader), just in case new template loader objects are added after creation.
    def wrapper(request, template, context=None, def_name=None, subdir='templates', content_type=None, status=None, charset=None):
        '''
        A shortcut to render a template.  This is one of the primary functions in the DMP framework.
        This method is added to the app space of each DMP-enabled app at load time.

            @request      The request context from Django.  If this is None, any TEMPLATE_CONTEXT_PROCESSORS defined in your settings
                          file will be ignored but the template will otherwise render fine.
            @template     The template file path to render.  This is relative to the app_path/controller_TEMPLATES_DIR/ directory.
                          For example, to render app_path/templates/page1, set template="page1.html", assuming you have
                          set up the variables as described in the documentation above.
            @context      A dictionary of name=value variables to send to the template page.  This can be a real dictionary
                          or a Django Context object.
            @def_name     Limits output to a specific top-level Mako <%block> or <%def> section within the template.
                          For example, def_name="foo" will call <%block name="foo"></%block> or <%def name="foo()"></def> within the template.
            @subdir       The sub-folder within the app where the template resides.  Templates are normally placed
                          in project/appname/templates/, which is the default value.
            @content_type The MIME type of the response.  Defaults to settings.DEFAULT_CONTENT_TYPE (usually 'text/html').
            @status       The HTTP response status code.  Defaults to 200 (OK).
            @charset      The charset to encode the processed template string (the output) with.  Defaults to settings.DEFAULT_CHARSET (usually 'utf-8').

        Returns a Django HttpResponse containing the rendered template.

        Examples of use from within appname/views/someview.py:

            from django_mako_plus import view_function

            @view_function
            def process_request(request):
                # return an HTML template in appname/templates/sometemplate.html
                return render_to_string(request, 'sometemplate.html', { 'var1': 'value' })

            @view_function
            def another_func(request):
                # return some dynamic JS in appname/scripts/sometemplate.js (which has embedded Mako code)
                return render_to_string(request, 'sometemplate.js', { 'var1': 'value' }, subdir="scripts")

            @view_function
            def yet_another(request):
                # return a single <block name="toolbar"> instead of the entire template in appname/templates/sometemplate.html
                return render_to_string(request, 'sometemplate.html', { 'var1': 'value' }, def_name='toolbar')

        The method triggers two signals:
            1. dmp_signal_pre_render_template: you can (optionally) return a new Mako Template object from a receiver to replace
               the normal template object that is used for the render operation.
            2. dmp_signal_post_render_template: you can (optionally) return a string to replace the string from the normal
               template object render.
        '''
        template_loader = get_dmp_instance().get_template_loader(app_name, subdir)
        template_adapter = template_loader.get_template(template)
        warnings.warn('As of DMP 4.2, `dmp_render` has changed to `request.dmp_render`. Please see the documentation for more information.', DeprecationWarning)
        return getattr(template_adapter, 'render_to_response')(context=context, request=request, def_name=def_name, content_type=content_type, status=status, charset=charset)

    # outer function return
    return wrapper

