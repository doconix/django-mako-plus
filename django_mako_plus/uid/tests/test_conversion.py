from unittest import TestCase
from datetime import datetime
import pytz
import random
from ..util import b58dec, b58enc, dt_to_millis, millis_to_dt


class ConversionTests(TestCase):
    #########################################
    ###   datetime <-> millis tests

    def test_naive(self):
        dt = datetime(2000, 6, 1, 2, 3, 4)
        millis = dt_to_millis(dt)
        dt2 = millis_to_dt(millis)
        self.assertEqual(dt, dt2)

    def test_utc(self):
        dt = datetime(2000, 6, 1, 2, 3, 4, tzinfo=pytz.utc)
        millis = dt_to_millis(dt)
        dt2 = millis_to_dt(millis).replace(tzinfo=pytz.utc)
        self.assertEqual(dt, dt2)

    def test_utc2(self):
        dt = datetime(2000, 6, 1, 2, 3, 4, tzinfo=pytz.timezone('US/Pacific'))
        millis = dt_to_millis(dt)
        dt2 = millis_to_dt(millis).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific'))
        self.assertEqual(dt, dt2)


    #########################################
    ###   Base58 testing

    def test_b58(self):
        nums = [ random.randint(0, 2**63) for i in range(100) ]
        enc = [ b58enc(n) for n in nums ]
        nums2 = [ b58dec(e) for e in enc ]
        self.assertEqual(nums, nums2)
