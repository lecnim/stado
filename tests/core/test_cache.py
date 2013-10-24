import os

from stado.core.content.cache import ShelveCache
from tests import TestTemporaryDirectory


class TestShelveCache(TestTemporaryDirectory):
    """
    Important!
    This test creates temporary directory which is available as self.temp_path.
    """

    def test_dict(self):

        cache = ShelveCache(self.temp_path)
        cache['a'] = 1

        self.assertEqual(1, cache['a'])
        # Test if files were created.
        self.assertTrue(os.listdir(self.temp_path))


    def test_files_property(self):

        cache = ShelveCache(self.temp_path)
        cache['a'] = 1
        cache['a'] = 1
        cache['a'] = 1

        cache['b'] = 1
        cache['c'] = 1

        cache['d'] = 1
        del cache['d']

        self.assertCountEqual(['a', 'b', 'c'], cache.files)
