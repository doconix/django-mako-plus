###########################################################################################
###   Converter of Base10 (decimal) to Base58
###   Ambiguous chars not used: 0, O, I, and l
###   This uses the same alphabet as bitcoin.

BASE58CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE58INDEX = { ch: i for i, ch in enumerate(BASE58CHARS) }

def b58enc(uid):
    '''Encodes a UID to an 11-length string, encoded using base58 url-safe alphabet'''
    # note: i tested a buffer array too, but string concat was 2x faster
    if not isinstance(uid, int):
        raise ValueError('Invalid integer: {}'.format(uid))
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
        raise ValueError('Cannot decode this type: {}'.format(enc_uid))
    uid = 0
    try:
        for i, ch in enumerate(enc_uid):
            uid = (uid * 58) + BASE58INDEX[ch]
    except KeyError:
        raise ValueError('Invalid character: "{}" ("{}", index 5)'.format(ch, enc_uid, i))
    return uid
