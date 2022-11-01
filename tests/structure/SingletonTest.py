import unittest

from walletflow.dags.common_package.structure.Singleton import Singleton


class DummySingleton(Singleton):
    _count_creation_attempts: int = 0

    def __init__(self):
        self._count_creation_attempts += 1

    @property
    def creations(self):
        return self._count_creation_attempts

    def reset(self):
        self._reset()


class SingletonTest(unittest.TestCase):
    def test_a_is_singleton(self):

        dummy = DummySingleton()
        self.assertEqual(1, dummy.creations, "Was created only once until now!")

        dummy2 = DummySingleton()
        self.assertEqual(2, dummy2.creations, "Second creation, should be 2")

    def test_b_dummy_reset(self):
        dummy3 = DummySingleton()
        self.assertEqual(3, dummy3.creations, "Third creation, should be 3")
        dummy3.reset()

        dummy4 = DummySingleton()
        self.assertEqual(1, dummy4.creations, "Reseted! Should be 1")
