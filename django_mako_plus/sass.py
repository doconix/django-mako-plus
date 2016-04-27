from mako.lexer import Lexer
from mako import parsetree

from .util import DMP_OPTIONS, run_command

import glob, sys, os, os.path, subprocess, itertools, re, base64


__doc__ = '''
Compiles scss files using the Sass runtime arguments in settings.py.

Also compiles scssm files, which are scss files with embedded Mako.
Only ${ var } expressions are supported right now.  Other Mako
constructs like <% %> may be supported later.
'''


MAKO_EXPRESSION_MARKERS = ( 'MakoExpression', 'ExpressionMako' )
RE_MAKO_EXPRESSION = re.compile('{}_(.+?)_{}'.format(MAKO_EXPRESSION_MARKERS[0], MAKO_EXPRESSION_MARKERS[1]), flags=re.MULTILINE)


def compile_scss_file(scss_file, css_file):
    '''
    Compiles a regular scss file

    If the Sass execution fails, this function raises subprocess.CalledProcessError.
    '''
    # run sass on it
    run_command(DMP_OPTIONS.get('RUNTIME_SCSS_ARGUMENTS') + [ scss_file, css_file ])


def compile_scssm_file(scssm_file, css_file):
    '''
    Compiles an scssm (sass with embedded Mako) file.
    This method works by replacing Mako codes with

    If the Sass execution fails, this function raises subprocess.CalledProcessError.
    '''
    # this algorithm isn't terribly fast, but it only runs the first time the file is accessed on a production system

    # read the contents of the file
    with open(scssm_file) as fin:
        contents = fin.read()
    try:
        # make a backup just in case something goes wrong
        # backup_scss = '{}.bak'.format(scssm_file)
        # with open(backup_scss, 'w') as fout:
        #     fout.write(contents)
        # embed mako codes in markers that are acceptable to sass
        with open(scssm_file, 'w') as fout:
            for node in Lexer(text=contents).parse().nodes:
                if isinstance(node, parsetree.Expression):
                    fout.write('{}_{}_{}'.format(MAKO_EXPRESSION_MARKERS[0], encode32(node.text), MAKO_EXPRESSION_MARKERS[1]))
                elif isinstance(node, parsetree.Text):
                    fout.write(node.content)
        # run sass on it
        compile_scss_file(scssm_file, css_file)
        # read the contents of the generated file
        with open(css_file) as fin:
            csscontents = fin.read()
        # unencode all the mako expressions
        csscontents = RE_MAKO_EXPRESSION.sub(lambda match: '${{{}}}'.format(decode32(match.group(1))), csscontents)
        # write the contents
        with open(css_file, 'w') as fout:
            fout.write(csscontents)
        # erase the backup
        os.remove(backup_scss)

    finally:
        # replace the original contents back in the scss file
        with open(scssm_file, 'w') as fout:
            fout.write(contents)



######################################################
###   Utilities used in this module
###   Using Base32 because its alphabet conforms to
###   CSS selectors.

def encode32(st):
    '''Encodes the given string to base64.'''
    if not isinstance(st, bytes):
        st = st.encode('utf8')              # we now have a byte string rather than the original unicode text
    b32_byte_st = base64.b32encode(st)   # we now have a base32-encoded byte string representing the text
    return b32_byte_st.decode('ascii').replace('=', '9')    # we're now back to Unicode (using ascii decoding since base64 is all ascii characters)


def decode32(st):
    '''Decodes the given base64-encoded string.'''
    st = st.replace('9', '=')
    if not isinstance(st, bytes):
        st = st.encode('ascii')     # we now have a byte string of the base64-encoded text instead of the Unicode base32s-encoded st
    byte_st = base64.b32decode(st)   # we now have a byte string of the original text
    return byte_st.decode('utf8')         # we now have a Unicode string of the original text
