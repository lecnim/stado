import unittest
import os
import tempfile
import shutil

from utilities import copytree


class TestCommand(unittest.TestCase):
    """Base class for testing commands."""

    def setUp(self):

        # Path pointing to current working directory.
        self.cwd = os.getcwd()

        # Path to commands test directory.
        self.path = os.path.dirname(__file__)

        # Path to temporary directory with sites.
        self.temp_path = tempfile.mkdtemp()
        copytree(os.path.join(self.path, 'sites'), self.temp_path)

        # Set current working directory to temporary directory with sites.
        os.chdir(self.temp_path)

    def tearDown(self):

        # Go to previous working directory and clear files.
        os.chdir(self.cwd)
        shutil.rmtree(self.temp_path)
