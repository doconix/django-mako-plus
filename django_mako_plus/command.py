from .util import log

import os, os.path
import sys
import subprocess
import time





################################################################
###   Run a shell commands

def run_command(*args, raise_exception=True):
    '''
    Runs a command, piping all output to the DMP log.
    The args should be separate arguments so paths and subcommands can have spaces in them:

        run_command('ls', '-l', '/Users/me/My Documents')

    On Windows, the PATH is not followed.  This can be overcome with:

        import shutil
        run_command(shutil.which('program'), '-l', '/Users/me/My Documents')
    '''
    log.info('%s', ' '.join(args))
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stdout:
        log.info('%s', stdout.decode('utf8'))
    if raise_exception and p.returncode != 0:
        if sys.version_info >= (3, 5):
            raise subprocess.CalledProcessError(p.returncode, args, output=stdout.decode('utf8'), stderr=stderr.decode('utf8'))
        else:
            raise subprocess.CalledProcessError(p.returncode, args)
    return p.returncode



