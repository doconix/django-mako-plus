from django.apps import apps, AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import os, os.path, subprocess, sys



# this is populated with the dictionary of options in engine.py when
# Django initializes the template engine
DMP_OPTIONS = {}

# the key for the DMP singleton engine instance (stored in DMP_OPTIONS by engine.py)
DMP_INSTANCE_KEY = 'django_mako_plus_instance'

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


def run_command(cmd_parts, raise_exception=True):
    '''
    Runs a command, piping all output to the DMP log.  The cmd_parts should be a sequence so paths can have spaces and we are os independent.
    '''
    log.info('%s' % ' '.join(cmd_parts))
    p = subprocess.Popen(cmd_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stdout:
        log.info('%s' % stdout.decode('utf8'))
    if raise_exception and p.returncode != 0:
        if sys.version_info >= (3, 5):
            raise subprocess.CalledProcessError(p.returncode, cmd_parts, output=stdout.decode('utf8'), stderr=stderr.decode('utf8'))
        else:
            raise subprocess.CalledProcessError(p.returncode, cmd_parts)
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
