import collections
import zlib


def merge_dicts(*dicts):
    '''
    Shallow merges an arbitrary number of dicts, starting
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
