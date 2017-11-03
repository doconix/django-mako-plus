from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

import base64


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
    This method does not use the registry cache.  Instead, it looks through all Django apps in settings.py and
    yields any with "DJANGO_MAKO_PLUS = True" in its __init__.py.
    '''
    for config in apps.get_app_configs():
        # check for the DJANGO_MAKO_PLUS = True in the app (should be in app/__init__.py)
        if getattr(config.module, 'DJANGO_MAKO_PLUS', False):
            yield config



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
        return self.get(idx, '')

    def get(self, idx, default=''):
        '''Returns the element at idx, or default if idx is beyond the length of the list'''
        # if the index is beyond the length of the list, return ''
        if isinstance(idx, int) and (idx >= len(self) or idx < -1 * len(self)):
            return default
        # else do the regular list function (for int, slice types, etc.)
        return super().__getitem__(idx)



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


def merge_dicts(*dicts):
    '''
    Merges an arbitrary number of dicts, starting 
    with the first argument and updating through the
    last argument (last dict wins on conflicting keys).
    '''
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged
    
  