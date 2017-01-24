from django.conf import settings
from django.template import Context, RequestContext, engines

from .util import log

import logging, hashlib



############################################################################
###   Rendering template blocks in other syntax languages

def django_syntax(context):
    '''
    A Mako filter that renders a block of text using the standard Django template engine.
    The Django template engine must be listed in settings.TEMPLATES.

    ## Simple expression in Django syntax:
    ${ '{{ name }}' | django_syntax(context) }

    ## Embedded code block:
    <%block filter="django_syntax(context)">
        {% for story in story_list %}
            <h2>
                {{ story.headline|upper }}
            </h2>
        {% endfor %}
    </%block>

    '''
    return template_syntax(context, using='django')


def jinja2_syntax(context):
    '''
    A Mako filter that renders a block of text using the Jinja2 template engine.
    The Jinja2 template engine must be listed in settings.TEMPLATES.

    ## Simple expression in Jinja2 syntax:
    ${ '{{ name }}' | jinja2_syntax(context) }

    ## Embedded Jinja2 code block:
    <%block filter="jinja2_syntax(context)">
        {% for item in navigation %}
            <li><a href="{{ item.href }}">{{ item.caption }}</a></li>
        {% endfor %}
    </%block>

    '''
    return template_syntax(context, using='jinja2')


def template_syntax(context, using='django'):
    '''
    A Mako filter that renders a block of text using a different template engine
    than Mako.  The named template engine must be listed in settings.TEMPLATES.

    Rendering Django or Jinja2 templates can be done more directly with
    `django_syntax` and `jinja2_syntax`.

    ## Simple expression in Mustache syntax:
    ${ '{{ name }}' | template_syntax(context, using='django_mustache') }

    ## Embedded Mustache code block:
    <%block filter="template_syntax(context, using='django_mustache')">
        {{#repo}}
            <b>{{name}}</b>
        {{/repo}}
        {{^repo}}
            No repos :(
        {{/repo}}
    </%block>

    '''
    # get the request (the MakoTemplateAdapter above places this in the context)
    request = context['request'] if isinstance(context, RequestContext) else None
    # get the current Mako template object so we can attach the compiled string for later use
    # Mako caches and automatically recreates this if the file changes
    mako_template = context['local'].template
    if not hasattr(mako_template, '__ns__render_django'):
        mako_template.__ns__render_django = {}

    # create a closure so we can still get to context and using (Mako filters take exactly one parameter: the string to filter)
    def wrap(template_st):
        # get the template object, or create and cache it
        key = hashlib.md5(template_st.encode('utf8'))
        try:
            template = mako_template.__ns__render_django[key]
        except KeyError:
            engine = engines[using]
            template = engine.from_string(template_st)
            self.mako_template.__ns__render_django[key] = template

        # create a copy the context
        dcontext = dict(context)

        # print a debug statement to the log
        if log.isEnabledFor(logging.DEBUG):
            log.info('rendering alternate syntax block using "{}" template engine'.format(using))

        # render the template with the context
        return template.render(context=dcontext, request=request)

    # return the embedded function
    return wrap

