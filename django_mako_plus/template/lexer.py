from django.apps import apps
from django.utils.html import conditional_escape
from django.utils.encoding import force_text

from mako.lexer import Lexer
from mako import parsetree, ast

from ..util import log
from ..tags import is_autoescape


###########################################################
###  DMP hook for expression filters. This allows DMP
###  to filter expressions ${...} after all other filters
###  have been run.
###
###  Currently, the use of this hook is HTML autoescaping.
###  Django autoescapes by default, while Mako does not.
###  DMP injects autoescaping to be consistent with Django.
###

MAKO_ESCAPE_REPLACEMENTS = {
    'h': 'django.utils.html.escape',  # uses Django's escape rather than Mako's, which works better with marks
}

class DMPLexer(Lexer):
    '''
    Subclass of Mako's Lexer, which is used during compilation of
    templates.  This subclass injects `process_exception()`
    as the final filter on every expression.  Overriding append_node()
    is a hack, but it's the only way I can find to hook into Mako's
    compile process without modifying Mako directly.
    '''
    def append_node(self, nodecls, *args, **kwargs):
        # fyi, this method runs on template compilation (not on template render)
        if nodecls == parsetree.Expression:
            # when an Expression, args[1] is a comma-separated string of filters
            # parse the filters and make any DMP replacements for them
            try:
                # this is Mako's ast, not the python one
                filters = [ MAKO_ESCAPE_REPLACEMENTS.get(f, f) for f in ast.ArgumentList(args[1]).args ]
            except Exception as e:
                log.warning('An error occurred when compiling the filters on an expression; allowing through so Mako can handle it (%s)', e)
                filters = []
            extra = {}  # extra info sent to the expression processor

            # if we have the 'n' filter, send that to the expression processor
            if 'n' in filters:
                extra['n_filter_on'] = True

            # add the expression processor as the last filter to be run
            # then recreate the args tuple
            filters.append('django_mako_plus.ExpressionPostProcessor(self' + \
                           (", extra={}".format(extra) if len(extra) > 0 else '') + \
                           ')')
            args = args[:1] + (','.join(filters),) + args[2:]
        return super().append_node(nodecls, *args, **kwargs)


# this is used read-only, so it can be in __init__ signature
EMPTY_DICT = {}

class ExpressionPostProcessor(object):
    '''
    Object that is called as the final filter on every template
    expression ${...}.  When created, the object keeps the
    context so it can be used later when the filter is run by Mako.

    Right now this object only does autoescaping. However, it is placed
    on *every* expression so we have a hook for future post-processing
    of expressions.

    See the creation of this object in DMPLexer above for more info.
    '''
    def __init__(self, tself, extra=EMPTY_DICT):
        # check whether it's on for this block
        self.html_escape = is_autoescape(tself.context)
        # the 'n' filter turns off our normal html escaping
        if extra.get('n_filter_on', False):
            self.html_escape = False
        # mark_safe() is handled in Django's conditional_escape(), so no need to deal with it
        # check the global setting
        dmp = apps.get_app_config('django_mako_plus')
        if not dmp.options['AUTOESCAPE']:
            self.html_escape = False

    def __call__(self, text):
        '''
        Mako calls this after evaluating the expression and applying
        all other filters.

        Right now this html escapes the expression, unless autoescape
        is toggled off.
        '''
        # we apply this across the board, even if the `n` filter is present because
        # DMP always creates unicode (see adapter.py where render_unicode() is used)
        text = force_text(text)

        # html encoding
        if self.html_escape:
            text = conditional_escape(text)  # internally, this honors mark_safe()

        return text
