import unittest
import os
import tempfile
import shutil


def copytree(source, destination):
    """Same as shutil.copytree(), but can copy to already existing
    directory."""

    if not os.path.exists(destination):
        os.makedirs(destination)

    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(destination, item)

        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)


class TestCommand(unittest.TestCase):

    def setUp(self):

        # Path pointing to current working directory.
        self.cwd = os.getcwd()

        self.path = os.path.dirname(__file__)
        self.temp_path = tempfile.mkdtemp()
        copytree(os.path.join(self.path, 'sites'), self.temp_path)

        os.chdir(self.temp_path)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.temp_path)

