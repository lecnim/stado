"""Tests command: new"""

import os

from stado.console.new import script, index
from stado.console import Console, CommandError
from tests.console import TestCommand


class TestNewSite(TestCommand):
    """Command new <site>:

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    def test_returned_value(self):
        """should return True if building successful."""

        self.assertTrue(Console().__call__('new test'))


    def test(self):
        """should correctly creates new site files."""

        Console().__call__('new test')

        self.assertTrue(os.path.exists(os.path.join(self.temp_path, 'a')))


        with open(os.path.join(self.temp_path, 'test', 'site.py')) as file:
            self.assertEqual(script, file.read())

        with open(os.path.join(self.temp_path, 'test', 'index.html')) as file:
            self.assertEqual(index, file.read())


    def test_site_exists(self):
        """should raise error when creating site which already exits."""

        self.assertFalse(Console().__call__('new a'))
        self.assertRaises(CommandError, Console().commands['new'].run, 'a')
