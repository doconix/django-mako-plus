from unittest import TestCase
from datetime import datetime
from ..muid import generate, SHARD_ID
from ..util import pack, unpack

class UidTests(TestCase):

    #########################################
    ###   Uid tests

    def test_uid(self):
        # generate 100 uids, make sure they are unique
        uids = set(( generate() for i in range(100) ))
        self.assertEqual(len(uids), 100)

    def test_pack_unpack(self):
        uid1 = generate()
        uid2 = generate()
        # unpack
        dt, counter, shard_id = unpack(uid1)
        dt2, counter2, shard_id2 = unpack(uid2)
        self.assertLess((dt2 - dt).total_seconds(), 10)  # two dates within 10 seconds of each other
        self.assertLess((datetime.utcnow() - dt).total_seconds(), 10)      # date within 10 seconds of UTC now
        self.assertEqual(counter + 1, counter2)
        self.assertEqual(shard_id, SHARD_ID)
        # pack
        self.assertEqual(uid1, pack(dt, counter, shard_id))
        self.assertEqual(uid2, pack(dt2, counter2, shard_id2))
