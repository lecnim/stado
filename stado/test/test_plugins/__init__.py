import unittest
import os
import tempfile
import shutil

class TestPlugin(unittest.TestCase):

    def setUp(self):
        self.path = os.path.dirname(__file__)
        self.temp_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_path)
