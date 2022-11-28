import unittest

from walletflow.dags.lazyutils.random.Randomize import random_string


class RandomTest(unittest.TestCase):
    def test_randomstring(self):
        s = random_string(1)
        self.assertEquals(1, len(s), "Expected a string with size 1")

        s2 = random_string(15)
        self.assertEquals(15, len(s2), "Expected a string with size 1")

        s3 = random_string(11)
        self.assertTrue(s3.isalnum(), "Should be alphanumeric")
