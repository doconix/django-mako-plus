from django.test import TestCase
from django_mako_plus.util import encode32, decode32
import random, string


class Tester(TestCase):

    def test_encode_decode_32(self):
        original = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2048))
        encoded = encode32(original)
        decoded = decode32(encoded)
        self.assertEqual(original, decoded)

