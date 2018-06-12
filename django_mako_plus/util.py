from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import base64
import os, os.path
import collections
import zlib
import re
from importlib import import_module



# set up the logger
import logging
log = logging.getLogger('django_mako_plus')



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


##########################################
###   Utilities

def import_qualified(name):
    '''
    Imports a fully-qualified name from a module:

        cls = import_qualified('homepage.views.index.MyForm')

    Raises an ImportError if it can't be ipmorted.
    '''
    parts = name.rsplit('.', 1)
    if len(parts) != 2:
        raise ImportError('Invalid fully-qualified name: {}'.format(name))
    try:
        return getattr(import_module(parts[0]), parts[1])
    except AttributeError:
        raise ImportError('{} not found in module {}'.format(parts[1], parts[0]))


def merge_dicts(*dicts):
    '''
    Merges an arbitrary number of dicts, starting
    with the first argument and updating through the
    last argument (last dict wins on conflicting keys).
    '''
    merged = {}
    for d in dicts:
        if d:
            merged.update(d)
    return merged


def flatten(*args):
    '''Generator that recursively flattens embedded lists, tuples, etc.'''
    for arg in args:
        if isinstance(arg, collections.Iterable) and not isinstance(arg, (str, bytes)):
            yield from flatten(*arg)
        else:
            yield arg


def split_app(path):
    '''
    Splits a file path on the app, returning (app config, relative path within app).
    '''
    parts = os.path.abspath(path).split(os.path.sep)
    for i in reversed(range(0, len(parts) - 1)):
        appdir, appname, filepath = os.path.sep.join(parts[:i]), parts[i], os.path.sep.join(parts[i + 1:])
        config = apps.app_configs.get(appname)
        if config is not None and os.path.samefile(config.path, appdir + os.path.sep + appname):
            # got it!
            return config, filepath
    # not found
    return None, path


def crc32(filename):
    '''
    Calculates the CRC checksum for a file.
    Using CRC32 because security isn't the issue and don't need perfect noncollisions.
    We just need to know if a file has changed.

    On my machine, crc32 was 20 times faster than any hashlib algorithm,
    including blake and md5 algorithms.
    '''
    result = 0
    with open(filename, 'rb') as fin:
        while True:
            chunk = fin.read(48)
            if len(chunk) == 0:
                break
            result = zlib.crc32(chunk, result)
    return result


EMPTY = object()
def getdefaultattr(obj, name, default=None, factory=EMPTY):
    '''
    Gets the given attribute from the object,
    creating it with a default or by calling
    a factory if needed.
    '''
    try:
        return getattr(obj, name)
    except AttributeError:
        pass
    val = factory() if factory is not EMPTY else None
    setattr(obj, name, val)
    return val


def qualified_name(obj):
    '''Returns the fully-qualified name of the given object'''
    if not hasattr(obj, '__module__'):
        obj = obj.__class__
    module = obj.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__qualname__
    return '{}.{}'.format(module, obj.__qualname__)
