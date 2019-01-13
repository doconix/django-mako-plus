import threading
from datetime import datetime
import os
import random
from . import COUNTER_BITS
from .util import b58enc, pack, infinite_counter


MUID_LOCK = threading.RLock()
COUNTER = infinite_counter(0, 2 ** COUNTER_BITS)
SHARD_ID = os.getpid() % 255


def generate(encode=False):
    '''
    Returns a 64-bit (8-byte) uid as an integer.
    This type of uid is guaranteed unique within a given machine.
    '''
    with MUID_LOCK:
        uid = pack(
            datetime.utcnow(),
            next(COUNTER),
            SHARD_ID,
        )
        if encode:
            return b58enc(uid)
        return uid
