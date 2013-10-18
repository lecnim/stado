import unittest
import tempfile
import shutil

class TestTemporaryDirectory(unittest.TestCase):

    def setUp(self):
        self.temp_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_path)