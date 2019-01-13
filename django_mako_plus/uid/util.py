from datetime import datetime, timedelta
import pytz
import random
from . import TIME_BITS, COUNTER_BITS, SHARD_BITS, TIME_MASK, COUNTER_MASK, SHARD_MASK


###########################################################################################
###  UID <--> (datetime, counter, shard)

def unpack(uid):
    '''Unpacks a uid (int or base58-encoded string)'''
    if isinstance(uid, (str, bytes)):
        uid = b58dec(uid)
    # mask and shift
    return (
        millis_to_dt((uid & TIME_MASK) >> (COUNTER_BITS + SHARD_BITS)),
        (uid & COUNTER_MASK) >> SHARD_BITS,
        (uid & SHARD_MASK),
    )

def pack(dt, counter, shard):
    '''Packs a uid into an integer'''
    return ( round(dt_to_millis(dt)) << (COUNTER_BITS + SHARD_BITS) ) +\
           ( counter << SHARD_BITS ) +\
           ( shard )


###########################################################################################
###   Converter to Base58
###   Ambiguous chars not used: 0, O, I, and l
###   This uses the same alphabet as bitcoin.

BASE58CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE58INDEX = { ch: i for i, ch in enumerate(BASE58CHARS) }

def b58enc(uid):
    '''Encodes a UID to an 11-length string, encoded using base58 url-safe alphabet'''
    # note: i tested a buffer array too, but string concat was 2x faster
    if not isinstance(uid, int):
        raise Base58Error('Invalid integer: {}'.format(uid))
    if uid == 0:
        return BASE58CHARS[0]
    enc_uid = ""
    while uid:
        uid, r = divmod(uid, 58)
        enc_uid = BASE58CHARS[r] + enc_uid
    return enc_uid

def b58dec(enc_uid):
    '''Decodes a UID from base58, url-safe alphabet back to int.'''
    if isinstance(enc_uid, str):
        pass
    elif isinstance(enc_uid, bytes):
        enc_uid = enc_uid.decode('utf8')
    else:
        raise Base58Error('Cannot decode this type: {}'.format(enc_uid))
    uid = 0
    try:
        for i, ch in enumerate(enc_uid):
            uid = (uid * 58) + BASE58INDEX[ch]
    except KeyError:
        raise Base58Error('Invalid character: "{}" ("{}", index 5)'.format(ch, enc_uid, i))
    return uid

class Base58Error(Exception):
    pass



###########################################################################################
###  Infinite counter

def infinite_counter(minval, maxval):
    '''
    Counter that starts at a random place between minval and maxval
    and then generates forever by wrapping around to minval when it hits maxval.
    '''
    i = random.randint(0, maxval)      # start at a random place
    while True:
        if i >= maxval:
            i = minval
        yield i
        i += 1


############################################################################################
###   Epoch converting

def dt_to_millis(dt):
    '''
    Returns the millis since unix UTC epoch.
    If dt is timezone-aware, it is converted to UTC before conversion to millis.
    If dt is naive, it is assumed to be UTC.
    '''
    if dt.tzinfo:
        dt = dt.astimezone(pytz.utc).replace(tzinfo=None)
    return 1000 * (dt - datetime(1970, 1, 1)) / timedelta(seconds=1)


def millis_to_dt(millis):
    '''
    Returns a naive datetime for the given millis since unix UTC epoch.
    The input millis must always be since UTC, not another time zone epoch.
    The return datetime will be naive (but essentially UTC), so to make it aware
    use:
        millis_to_datetime(...).replace(tzinfo=pytz.utc)

    To make the datetime aware with a different timezone:
        dt = millis_to_datetime(...).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Eastern'))
    '''
    return datetime.utcfromtimestamp(millis / 1000)
