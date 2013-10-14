import unittest
import os
import tempfile
import shutil

from stado.stado import Site

class TestSite(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), 'test_loader')

        self.temp_path = tempfile.mkdtemp()
        print(self.temp_path)

    def tearDown(self):
        shutil.rmtree(self.temp_path)


    def test_load(self):

        site = Site(self.path, config={'destination': self.temp_path})
        returned = site.load()

        self.assertTrue(returned)

        fp = os.path.join(self.temp_path, 'a.html')
        self.assertTrue(os.path.exists(fp))
        with open(fp) as file:
            self.assertEqual('hello world', file.read())

        self.assertTrue(os.path.exists(os.path.join(self.temp_path, 'b.html')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_path, 'c.html')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_path, 'd.jpg')))
        self.assertTrue(
            os.path.exists(os.path.join(self.temp_path, 'tree', 'a.html')))
        self.assertTrue(
            os.path.exists(os.path.join(self.temp_path, 'tree', 'a', 'b.html')))