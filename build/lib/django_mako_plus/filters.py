from django.template import RequestContext, engines

from .util import log




############################################################################
###   Rendering template blocks in other syntax languages

def django_syntax(local, **kwargs):
    '''
    A Mako filter that renders a block of text using the standard Django template engine.
    The Django template engine must be listed in settings.TEMPLATES.

    The template context variables are available in the embedded template.
    Specify kwargs to add additional variables created within the template.

    ## Simple expression in Django syntax:
    ${ '{{ name }}' | django_syntax(local) }

    ## Embedded code block:
    <%block filter="django_syntax(local)">
        {% for story in story_list %}
            <h2>
                {{ story.headline|upper }}
            </h2>
        {% endfor %}
    </%block>

    '''
    return alternate_syntax(local, 'django', **kwargs)


def jinja2_syntax(local, **kwargs):
    '''
    A Mako filter that renders a block of text using the Jinja2 template engine.
    The Jinja2 template engine must be listed in settings.TEMPLATES.

    The template context variables are available in the embedded template.
    Specify kwargs to add additional variables created within the template.

    ## Simple expression in Jinja2 syntax:
    ${ '{{ name }}' | jinja2_syntax(local) }

    ## Embedded Jinja2 code block:
    <%block filter="jinja2_syntax(local)">
        {% for item in navigation %}
            <li><a href="{{ item.href }}">{{ item.caption }}</a></li>
        {% endfor %}
    </%block>

    '''
    return alternate_syntax(local, 'jinja2', **kwargs)


def alternate_syntax(local, using, **kwargs):
    '''
    A Mako filter that renders a block of text using a different template engine
    than Mako.  The named template engine must be listed in settings.TEMPLATES.

    The template context variables are available in the embedded template.
    Specify kwargs to add additional variables created within the template.

    The following examples assume you have installed the django_mustache template
    engine in settings.py:

        ## Simple expression in Mustache syntax:
        ${ '{{ name }}' | template_syntax(local, 'django_mustache') }

        ## Embedded Mustache code block:
        <%block filter="template_syntax(local, 'django_mustache')">
            {{#repo}}
                <b>{{name}}</b>
            {{/repo}}
            {{^repo}}
                No repos :(
            {{/repo}}
        </%block>

    Rendering Django or Jinja2 templates should be done with `django_syntax` and
    `jinja2_syntax` because it doesn't require the using parameter.
    '''
    # get the request (the MakoTemplateAdapter above places this in the context)
    request = local.context['request'] if isinstance(local.context, RequestContext) else None
    # get the current Mako template object so we can attach the compiled string for later use
    # Mako caches and automatically recreates this if the file changes
    mako_template = local.template
    if not hasattr(mako_template, '__compiled_template_syntax'):
        mako_template.__compiled_template_syntax = {}

    # create a closure so we can still get to context and using (Mako filters take exactly one parameter: the string to filter)
    def wrap(template_st):
        # get the template object, or create and cache it
        try:
            template = mako_template.__compiled_template_syntax[template_st]
        except KeyError:
            engine = engines[using]
            template = engine.from_string(template_st)
            # using full string, even if long, as the key doesn't really affect performance of python's hash (see http://stackoverflow.com/questions/28150047/efficiency-of-long-str-keys-in-python-dictionary)
            mako_template.__compiled_template_syntax[template_st] = template

        # create a copy the context and add any kwargs to it
        dcontext = dict(local.context)
        dcontext.update(kwargs)

        # print a debug statement to the log
        log.debug('rendering embedded expression or block using %s template engine', using)

        # render the template with the context
        return template.render(context=dcontext, request=request)

    # return the embedded function
    return wrap

