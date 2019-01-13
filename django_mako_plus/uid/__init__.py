LICENSE = 'Apache 2.0'
AUTHOR = 'Conan C. Albrecht <doconix@gmail.com'
VERSION = 1.3

#####################################################################################################
###   A UID is made up of 63 bits, giving a range of 2^63 = 9,223,372,036,854,775,807.
###
###   Bits are assigned as follows:
###   42 bits            | 13 bits  | 8 bits
###   millis since epoch | counter  | shard id
###
###   millis:   42 bits gives us 4,398,046,511,104 milliseconds or 139 years.
###             identifier.unpack(2**63 - 1) ==> May, 2109
###   counter:  13 bits gives us 8,192 possible ids per millisecond per shard.
###   shard id: 8 bits gives us 256 possible shards, which represent unique database instances,
###             web server instances, etc.
###
###   The highest possible UID (2**63 - 1) has the following widths:
###       Base 10   9223372036854775807     19 chars
###       Base 16   7fffffffffffffff        16 chars
###       Base 58   NQm6nKp8qFC             11 chars  (url-safe encoding, see `encode` function below)
###
###   The reason for a custom UID format (instead of standard UUIDs) is these are 64 bits. The standard
###   UUID range of 256 bits isn't needed here, and using it causes huge ids. These IDs fit within
###   the BIGINT size of most databases.
###

TIME_BITS =    42
COUNTER_BITS = 13
SHARD_BITS =   8
TIME_MASK =    (2**TIME_BITS    - 1) << (COUNTER_BITS + SHARD_BITS)   # 111111111111111111111111111111111111111111000000000000000000000
COUNTER_MASK = (2**COUNTER_BITS - 1) << (SHARD_BITS)                  # 000000000000000000000000000000000000000000111111111111100000000
SHARD_MASK =   (2**SHARD_BITS   - 1)                                  # 000000000000000000000000000000000000000000000000000000011111111

from .util import b58enc, millis_to_dt, dt_to_millis

##################################################
###  Public interface functions

# Machine-based uid
from .muid import generate as uid
