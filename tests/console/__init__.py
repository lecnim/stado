import unittest
import os
import tempfile
import shutil
import urllib
from stado.console import Console

from stado.utils import copytree

class TestCommandNew(unittest.TestCase):

    """A watch command"""

    command_class = None

    def setUp(self):

        # Path pointing to current working directory.
        self.cwd = os.getcwd()
        # Path to commands test directory.
        self.path = os.path.dirname(__file__)
        # Path to temporary directory with sites.
        self.temp_path = tempfile.mkdtemp()
        # Set current working directory to temporary directory with sites.
        os.chdir(self.temp_path)

        self.command = self.command_class()

    def tearDown(self):

        # Go to previous working directory and clear files.
        os.chdir(self.cwd)
        shutil.rmtree(self.temp_path)

    #
    # Shortcuts
    #

    def read_url(self, url, host, port):
        url = 'http://{}:{}/{}'.format(host, port, url)
        return urllib.request.urlopen(url).read().decode('UTF-8')

    def read_file(self, path):
        """Returns data from given path. Path must be relative to current
        temp path."""

        if os.path.isabs(path):
            raise ValueError('path must be relative!')

        fp = os.path.join(self.temp_path, *path.split('/'))
        self.assertTrue(os.path.exists(fp),
                        msg='path not found: ' + fp)
        with open(fp) as file:
            return file.read()

    def create_file(self, path, data='hello world'):
        """Creates a new file with a data. Use '/' as a path separator,
        path must be relative to temp."""

        if os.path.isabs(path):
            raise ValueError('path must be relative!')

        path = os.path.join(self.temp_path, *path.split('/'))
        dir_path = os.path.dirname(path)

        # Create missing dirs.
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(path, 'w') as file:
            file.write(data)

    def modify_file(self, path, data='UPDATE'):
        """Modifies a file data. Use '/' as a path separator,
        path must be relative to temp."""

        if os.path.isabs(path):
            raise ValueError('path must be relative!')

        with open(os.path.join(self.temp_path, *path.split('/')), 'w') as file:
            file.write(data)

    def remove_file(self, path):
        """BE CAREFUL! Removes given file. Use '/' as a path separator,
        path must be relative to temp."""

        if os.path.isabs(path):
            raise ValueError('path must be relative!')
        os.remove(os.path.join(self.temp_path, *path.split('/')))

    def remove_dir(self, path):
        """BE CAREFUL! Removes directory recursively. Use '/' as a path
        separator, path must be relative to temp."""


        if os.path.isabs(path):
            raise ValueError('path must be relative!')
        p = os.path.join(self.temp_path, *path.split('/'))
        shutil.rmtree(p)


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