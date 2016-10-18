from mako.lexer import Lexer
from mako import parsetree

from .exceptions import SassCompileException
from .util import DMP_OPTIONS, run_command, lock_file, encode32, decode32

import glob, sys, os, os.path, subprocess, itertools, re


__doc__ = '''
Compiles scss files using the Sass runtime arguments in settings.py.

Also compiles scssm files, which are scss files with embedded Mako.
Only ${ var } expressions are supported right now.  Other Mako
constructs like <% %> may be supported later.
'''


MAKO_EXPRESSION_MARKERS = ( 'MakoExpression', 'ExpressionMako' )
RE_MAKO_EXPRESSION = re.compile('{}_(.+?)_{}'.format(MAKO_EXPRESSION_MARKERS[0], MAKO_EXPRESSION_MARKERS[1]), flags=re.MULTILINE)


def check_template_scss(styles_dir, template_name):
    '''
    Checks to see if template.scss or template.scssm need compiling.
    The styles_dir should be the full path to the styles directory.
    The template_name should be the name of the template *without the extension*.

    Raises a SassCompileException if compilation fails.
    '''
    for ext in ( 'css', 'cssm' ):
        scss_file = os.path.join(styles_dir, '{}.s{}'.format(template_name, ext))
        gen_css_file = os.path.join(styles_dir, '{}.{}'.format(template_name, ext))
        try:
            scss_stat = os.stat(scss_file)
        except OSError:
            scss_stat = None
        if scss_stat != None:  # only continue this block if we found a .scss file
            try:
                fstat = os.stat(gen_css_file)
            except OSError:
                fstat = None
            # if we 1) have no css_file or 2) have a newer scss_file, run the compiler
            if fstat == None or scss_stat.st_mtime > fstat.st_mtime:
                try:
                    if ext == 'css':
                        compile_scss_file(scss_file, gen_css_file)
                    else:
                        compile_scssm_file(scss_file, gen_css_file)
                except subprocess.CalledProcessError as cpe:
                    raise SassCompileException(cpe.cmd, cpe.stderr)


def compile_scss_file(scss_file, css_file):
    '''
    Compiles a regular scss file

    If the Sass execution fails, this function raises subprocess.CalledProcessError.
    '''
    # run sass on it
    args = list(DMP_OPTIONS.get('RUNTIME_SCSS_ARGUMENTS'))
    args.append(scss_file)
    args.append(css_file)
    run_command(*args)


def compile_scssm_file(scssm_file, css_file):
    '''
    Compiles an scssm (sass with embedded Mako) file.
    This is a total hack to sneak mako codes through the Sass compiler.  The algorithm
    uses the Mako lexer to split the file, then it replaces Expressions in the file
    with Base32 -- that alphabet is valid throughout CSS rules.  After Sass does its thing,
    we switch the Base32 back to the Mako codes.

    If the Sass execution fails, this function raises subprocess.CalledProcessError.
    '''
    # this algorithm isn't terribly fast, but it only runs the first time the file is accessed on a production system
    # lock the file so other processes can't access it
    with lock_file(scssm_file):

        # read the contents of the file
        with open(scssm_file) as fin:
            contents = fin.read()

        try:
            # make a backup just in case something goes wrong (this is for testing)
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
            # os.remove(backup_scss)

        finally:
            # replace the original contents back in the scss file
            with open(scssm_file, 'w') as fout:
                fout.write(contents)
            # update the modified timestamp on the css file so the scssm_file is older than it (we just rewrote the scssm)
            os.utime(css_file)


