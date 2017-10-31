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
        raise CommandError(p.returncode, ' '.join(args), stdout.decode('utf8'), stderr.decode('utf8'))
    return p.returncode



class CommandError(Exception):
    def __init__(self, returncode, command, output, error):
        self.returncode = returncode
        self.command = command
        self.output = output
        self.error = error
        super().__init__()
        
    def __str__(self):
        return '[{}] {}\n{}\nCommand was: {}'.format(self.returncode, self.output, self.error, self.command)
