from django.apps import apps, AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import os, os.path, subprocess, sys, time, base64


# this is populated with the dictionary of options in engine.py when
# Django initializes the template engine
DMP_OPTIONS = {}

# the key for the DMP singleton engine instance (stored in DMP_OPTIONS by engine.py)
DMP_INSTANCE_KEY = 'django_mako_plus_instance'

# types of view functions
DMP_VIEW_ERROR = 0         # some type of exception
DMP_VIEW_FUNCTION = 1      # regular view function
DMP_VIEW_CLASS_METHOD = 2  # class-based as_view()
DMP_VIEW_TEMPLATE = 3      # view template

# set up the logger
import logging
log = logging.getLogger('django_mako_plus')



################################################################
###   Utility functions

def get_dmp_instance():
    '''
    Retrieves the DMP template engine instance.
    '''
    try:
        return DMP_OPTIONS[DMP_INSTANCE_KEY]
    except KeyError:
        raise ImproperlyConfigured('The Django Mako Plus template engine did not initialize correctly.  Check your logs for previous errors that may have caused initialization to fail, and check that DMP is set correctly in settings.py.')


def get_dmp_app_configs():
    '''
    Gets the DMP-enabled app configs, which will be a subset of all installed apps.  This is a generator function.
    '''
    for config in apps.get_app_configs():
        # check for the DJANGO_MAKO_PLUS = True in the app (should be in app/__init__.py)
        if getattr(config.module, 'DJANGO_MAKO_PLUS', False):
            yield config


def run_command(*args, raise_exception=True):
    '''
    Runs a command, piping all output to the DMP log.
    The args should be separate arguments so paths and subcommands can have spaces in them:

        run_command('ls', '-l', '/Users/me/My Documents')

    On Windows, the PATH is not followed.  This can be overcome with:

        import shutil
        run_command(shutil.which('program'), '-l', '/Users/me/My Documents')
    '''
    log.info('%s' % ' '.join(args))
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stdout:
        log.info('%s' % stdout.decode('utf8'))
    if raise_exception and p.returncode != 0:
        if sys.version_info >= (3, 5):
            raise subprocess.CalledProcessError(p.returncode, args, output=stdout.decode('utf8'), stderr=stderr.decode('utf8'))
        else:
            raise subprocess.CalledProcessError(p.returncode, args)
    return p.returncode


################################################################
###   Special type of list used for url params

class URLParamList(list):
    '''
    A simple extension to Python's list that returns '' for indices that don't exist.
    For example, if the object is ['a', 'b'] and you call obj[5], it will return ''
    rather than throwing an IndexError.  This makes dealing with url parameters
    simpler since you don't have to check the length of the list.
    '''
    def __getitem__(self, idx):
        '''Returns the element at idx, or '' if idx is beyond the length of the list'''
        # if the index is beyond the length of the list, return ''
        if isinstance(idx, int) and (idx >= len(self) or idx < -1 * len(self)):
            return ''
        # else do the regular list function (for int, splice types, etc.)
        return list.__getitem__(self, idx)



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





######################################################
###   Encoding routines.
###   Using Base32 because its alphabet conforms to
###   CSS selectors.

def encode32(st):
    '''Encodes the given string to base64.'''
    if not isinstance(st, bytes):
        st = st.encode('utf8')              # we now have a byte string rather than the original unicode text
    b32_byte_st = base64.b32encode(st)   # we now have a base32-encoded byte string representing the text
    return b32_byte_st.decode('ascii').replace('=', '9')    # we're now back to Unicode (using ascii decoding since base32 is all ascii characters)


def decode32(st):
    '''Decodes the given base64-encoded string.'''
    st = st.replace('9', '=')
    if not isinstance(st, bytes):
        st = st.encode('ascii')     # we now have a byte string of the base64-encoded text instead of the Unicode base32s-encoded st
    byte_st = base64.b32decode(st)   # we now have a byte string of the original text
    return byte_st.decode('utf8')         # we now have a Unicode string of the original text


