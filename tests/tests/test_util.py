from django.test import TestCase
from django_mako_plus.util import encode32, decode32
from django_mako_plus.util import log
import random, string
import logging


class UtilTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # skip debug messages during testing
        cls.loglevel = log.getEffectiveLevel()
        log.setLevel(logging.WARNING)

    @classmethod
    def tearDownTestData(cls):
        # set log level back to normal
        log.setLevel(cls.loglevel)

    def test_encode_decode_32(self):
        original = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2048))
        encoded = encode32(original)
        decoded = decode32(encoded)
        self.assertEqual(original, decoded)

