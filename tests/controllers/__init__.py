import unittest
import shutil
import tempfile
import os
import inspect

from stado import Stado


class TestPlugin(unittest.TestCase):

    @property
    def path(self):
        return os.path.dirname(inspect.getfile(self.__class__))

    def setUp(self):
        self.cwd = os.getcwd()
        self.temp_path = tempfile.mkdtemp()

        self.app = Stado(os.path.join(self.path, 'data'),
                         output=self.temp_path)

        os.chdir(self.temp_path)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.temp_path)
