import unittest
import os
import tempfile
import shutil
import urllib
from stado.console import Console

from stado.utils import copytree


class TestCommand(unittest.TestCase):
    """Base class for testing commands."""

    data_path = 'data'
    _command = None

    def setUp(self):

        # Path pointing to current working directory.
        self.cwd = os.getcwd()

        # Path to commands test directory.
        self.path = os.path.dirname(__file__)

        # Path to temporary directory with sites.
        self.temp_path = tempfile.mkdtemp()
        copytree(os.path.join(self.path, self.data_path), self.temp_path)

        # Set current working directory to temporary directory with sites.
        os.chdir(self.temp_path)

        self.console = Console()

    def tearDown(self):

        # Go to previous working directory and clear files.
        os.chdir(self.cwd)
        shutil.rmtree(self.temp_path)

    def read_file(self, *path):
        """Returns data from given path, relative to current temp path."""

        fp = os.path.join(self.temp_path, *path)
        self.assertTrue(os.path.exists(fp),
                        msg='path not found: ' + fp)

        with open(fp) as file:
            return file.read()

    def read_url(self, url, host, port):
        url = 'http://{}:{}/{}'.format(host, port, url)
        return urllib.request.urlopen(url).read().decode('UTF-8')

    def command(self, arguments=''):
        """Execute console command with given arguments string."""
        return self.console(self._command + ' ' + arguments)