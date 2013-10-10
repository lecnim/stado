import unittest
import tempfile

from stado.stado import FileCache

class TestFileCache(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_dict(self):

        cache = FileCache(self.temp_dir)
        cache['a'] = 1

        self.assertEqual(1, cache['a'])

