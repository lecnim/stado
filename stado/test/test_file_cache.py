import unittest
import os
import tempfile
import shutil

from stado.stado import FileCache

class TestFileCache(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_dict(self):

        cache = FileCache(self.temp_dir)
        cache['a'] = 1

        self.assertEqual(1, cache['a'])
        # Test if files were created.
        self.assertTrue(os.listdir(self.temp_dir))
