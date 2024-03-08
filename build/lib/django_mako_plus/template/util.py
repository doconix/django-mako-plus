from django.apps import apps
from django.utils.html import mark_safe
from mako.exceptions import RichTraceback
from mako.template import Template as MakoTemplate
from mako.runtime import Context as MakoContext, _populate_self_namespace

import io
import os, os.path


def template_inheritance(obj):
    '''
    Generator that iterates the template and its ancestors.
    The order is from most specialized (furthest descendant) to
    most general (furthest ancestor).

    obj can be either:
        1. Mako Template object
        2. Mako `self` object (available within a rendering template)
    '''
    if isinstance(obj, MakoTemplate):
        obj = create_mako_context(obj)['self']
    elif isinstance(obj, MakoContext):
        obj = obj['self']
    while obj is not None:
        yield obj.template
        obj = obj.inherits


def create_mako_context(template_obj, **kwargs):
    # I'm hacking into private Mako methods here, but I can't see another
    # way to do this.  Hopefully this can be rectified at some point.
    kwargs.pop('self', None)  # some contexts have self in them, and it messes up render_unicode below because we get two selfs
    runtime_context = MakoContext(io.StringIO(), **kwargs)
    runtime_context._set_with_template(template_obj)
    _, mako_context = _populate_self_namespace(runtime_context, template_obj)
    return mako_context


def get_template_debug(template_name, error):
    '''
    This structure is what Django wants when errors occur in templates.
    It gives the user a nice stack trace in the error page during debug.
    '''
    # This is taken from mako.exceptions.html_error_template(), which has an issue
    # in Py3 where files get loaded as bytes but `lines = src.split('\n')` below
    # splits with a string. Not sure if this is a bug or if I'm missing something,
    # but doing a custom debugging template allows a workaround as well as a custom
    # DMP look.
    # I used to have a file in the templates directory for this, but too many users
    # reported TemplateNotFound errors. This function is a bit of a hack, but it only
    # happens during development (and mako.exceptions does this same thing).
    #   /justification
    stacktrace_template = MakoTemplate(r"""
<%! from mako.exceptions import syntax_highlight, pygments_html_formatter %>
<style>
    .stacktrace { margin:5px 5px 5px 5px; }
    .highlight { padding:0px 10px 0px 10px; background-color:#9F9FDF; }
    .nonhighlight { padding:0px; background-color:#DFDFDF; }
    .sample { padding:10px; margin:10px 10px 10px 10px;
                font-family:monospace; }
    .sampleline { padding:0px 10px 0px 10px; }
    .sourceline { margin:5px 5px 10px 5px; font-family:monospace;}
    .location { font-size:80%; }
    .highlight { white-space:pre; }
    .sampleline { white-space:pre; }

    % if pygments_html_formatter:
        ${pygments_html_formatter.get_style_defs() | n}
        .linenos { min-width: 2.5em; text-align: right; }
        pre { margin: 0; }
        .syntax-highlighted { padding: 0 10px; }
        .syntax-highlightedtable { border-spacing: 1px; }
        .nonhighlight { border-top: 1px solid #DFDFDF;
                        border-bottom: 1px solid #DFDFDF; }
        .stacktrace .nonhighlight { margin: 5px 15px 10px; }
        .sourceline { margin: 0 0; font-family:monospace; }
        .code { background-color: #F8F8F8; width: 100%; }
        .error .code { background-color: #FFBDBD; }
        .error .syntax-highlighted { background-color: #FFBDBD; }
    % endif

    ## adjustments to Django css
    table.source {
        background-color: #fdfdfd;
    }
    table.source > tbody > tr > th {
        width: auto;
    }
    table.source > tbody > tr > td {
        font-family: inherit;
        white-space: normal;
        padding: 15px;
    }
    #template {
        background-color: #b3daff;
    }

</style>
<%

    src = tback.source
    line = tback.lineno
    if isinstance(src, bytes):
        src = src.decode()
    if src:
        lines = src.split('\n')
    else:
        lines = None
%>
<h3>${tback.errorname}: ${tback.message}</h3>

% if lines:
    <div class="sample">
    <div class="nonhighlight">
    % for index in range(max(0, line-4),min(len(lines), line+5)):
        <%
        if pygments_html_formatter:
            pygments_html_formatter.linenostart = index + 1
        %>
        % if index + 1 == line:
        <%
        if pygments_html_formatter:
            old_cssclass = pygments_html_formatter.cssclass
            pygments_html_formatter.cssclass = 'error ' + old_cssclass
        %>
            ${lines[index] | n,syntax_highlight(language='mako')}
        <%
        if pygments_html_formatter:
            pygments_html_formatter.cssclass = old_cssclass
        %>
        % else:
            ${lines[index] | n,syntax_highlight(language='mako')}
        % endif
    % endfor
    </div>
    </div>
% endif

<div class="stacktrace">
% for (filename, lineno, function, line) in tback.reverse_traceback:
    <div class="location">${filename}, line ${lineno}:</div>
    <div class="nonhighlight">
    <%
       if pygments_html_formatter:
           pygments_html_formatter.linenostart = lineno
    %>
        <div class="sourceline">${line | n,syntax_highlight(filename)}</div>
    </div>
% endfor
</div>
""")
    tback = RichTraceback(error, error.__traceback__)
    lines = stacktrace_template.render_unicode(tback=tback)
    return {
        'message': '',
        'source_lines': [
            ( '', mark_safe(lines) ),
        ],
        'before': '',
        'during': '',
        'after': '',
        'top': 0,
        'bottom': 0,
        'total': 0,
        'line': tback.lineno or 0,
        'name': template_name,
        'start': 0,
        'end': 0,
    }
