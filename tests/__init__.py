import unittest
import tempfile
import shutil
import os
import inspect


class TestTemporaryDirectory(unittest.TestCase):

    def setUp(self):
        self.temp_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_path)



class TestInCurrentDirectory(unittest.TestCase):

    @property
    def path(self):
        return os.path.dirname(inspect.getfile(self.__class__))

    def setUp(self):
        self.cwd = os.getcwd()
        os.chdir(self.path)

    def tearDown(self):
        os.chdir(self.cwd)
