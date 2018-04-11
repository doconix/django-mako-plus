from .util import log

import os, os.path
import sys
import subprocess
import time
from collections import namedtuple


################################################################
###   Run a shell commands

ReturnInfo = namedtuple('CommandReturn', ( 'code', 'stdout', 'stderr' ))


def run_command(*args, raise_exception=True):
    '''
    Runs a command, piping all output to the DMP log.
    The args should be separate arguments so paths and subcommands can have spaces in them:

        ret = run_command('ls', '-l', '/Users/me/My Documents')
        print(ret.code)
        print(ret.stdout)
        print(ret.stderr)

    On Windows, the PATH is not followed.  This can be overcome with:

        import shutil
        run_command(shutil.which('program'), '-l', '/Users/me/My Documents')
    '''
    args = [ str(a) for a in args ]
    log.info('running %s', ' '.join(args))
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = p.communicate()
    returninfo = ReturnInfo(p.returncode, stdout.decode('utf8'), stderr.decode('utf8'))
    if stdout:
        log.info('%s', returninfo.stdout)
    if raise_exception and returninfo.code != 0:
        raise CommandError(' '.join(args), returninfo)
    return returninfo


class CommandError(Exception):
    def __init__(self, command, returninfo):
        self.command = command
        self.returninfo = returninfo
        super().__init__('CommandError')

    def __str__(self):
        return '[return value: {}] {}; {}'.format(self.returninfo.code, self.returninfo.stdout[:1000], self.returninfo.stderr[:1000])
