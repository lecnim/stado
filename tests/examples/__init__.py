import unittest
import shutil
import tempfile
import os
import inspect

from stado.console import Console


class TestExample(unittest.TestCase):

    @property
    def path(self):
        return os.path.dirname(inspect.getfile(self.__class__))

    def setUp(self):

        self.cwd = os.getcwd()
        os.chdir(self.path)

        self.temp_path = tempfile.mkdtemp()

        self.console = Console()
        self.console('build data --output ' + self.temp_path)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.temp_path)


