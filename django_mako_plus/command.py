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



#################################################################
###   File locking context manager - used by sass.py

class lock_file(object):
    '''
    A context manager that provides a non-blocking file lock on both Unix and Windows.
    Uses a temporary file for the lock - in the same directory as the filename.
    If the lock fails after timeout_seconds, an OSError is raised.

    I'm not using fcntl.flock because it is Unix-only and DMP is used on both
    Unix and Windows.  This is a very simplistic locking scheme, but it works
    for our purposes.
    '''
    def __init__(self, filename, timeout_seconds=5):
        self.filename = filename
        self.lock_filename = '{}.templock'.format(filename)
        self.timeout_seconds = timeout_seconds


    def __enter__(self):
        # acquire the lock to it
        for i in range(self.timeout_seconds):
            # create the lock file
            if not os.path.exists(self.lock_filename):
                self.fd = open(self.lock_filename, 'w')
                # we created successfully, so break out!
                break
            else:  # couldn't get the lock, so wait a second a try again
                time.sleep(1)
        else:  # we couldn't get a lock in timeout_seconds tries, so raise the exception
            raise OSError("Unable to acquire lock on {}; if you are sure no other processes are running, you may need to delete the lock file manually: {}".format(self.filename, self.lock_filename))
        # return
        return self


    def __exit__(self, exec_type, exec_val, exec_tb):
        # close and remove the temporary file
        self.fd.close()
        try:
            os.remove(self.lock_filename)
        except FileNotFoundError:  # shouldn't ever happen, but just in case
            pass

