import os

from stado.core.cache import ShelveCache
from tests import TestTemporaryDirectory


class TestShelveCache(TestTemporaryDirectory):
    """
    Important!
    This test creates temporary directory which is available as self.temp_path.
    """

    def test_dict(self):

        cache = ShelveCache(self.temp_path)
        cache.save('a', 1)

        self.assertEqual(1, cache.load('a'))
        # Test if files were created.
        self.assertTrue(os.listdir(self.temp_path))
