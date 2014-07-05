"""Tests command: new"""

import os
import textwrap

from stado.console.new import FILES, New
from stado.console import CommandError, Console
from tests.console import TestCommandNew


class TestNew(TestCommandNew):
    """Command new <site>:

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    command_class = New

    #
    # Integration tests.
    #

    def test_returned_value(self):
        """should return True if building successful."""

        self.assertTrue(self.command.run('new_site'))

    def test(self):
        """should correctly creates new site files."""

        self.command.run('test')

        self.assertTrue(os.path.exists('test'))
        for file_name, data in FILES.items():
            self.assertEqual(textwrap.dedent(data),
                             self.read_file('test/' + file_name))

    def test_site_exists(self):
        """should raise error when creating site which already exits."""

        self.create_file('new_site/hello')
        self.assertRaises(CommandError, self.command.run, 'new_site')

    #
    # Console integration.
    #

    def test_console(self):
        """should work with console"""

        console = Console()
        console(self.command_class.name + ' new_site')

        self.assertTrue(os.path.exists('new_site'))