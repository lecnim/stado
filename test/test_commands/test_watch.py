import os
import tempfile

from stado import config
from commands import CommandLineInterface
from test.test_commands import TestCommand



# Helpers.

def modify_file(path):
    """Append ' updated' data to given file."""
    with open(path, 'a') as file:
        file.write(' updated')

def create_file(path):
    """Creates new file with 'hello world' data."""
    with open(path, 'w') as file:
        file.write('hello world')



class TestWatchSite(TestCommand):
    """Tests: watch [site]

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    def setUp(self):
        TestCommand.setUp(self)

        self.shell = CommandLineInterface()
        # For faster checking files changes.
        self.shell.set_interval(0.1)
        # After first rebuild stop command.
        self.shell.after_rebuild = self.shell.stop_waiting



    def test_modify_file(self):
        """Watch command should rebuild site if site files were modified."""

        self.shell.before_waiting = (modify_file,
                                     [os.path.join(self.temp_path, 'a', 'a.html')])
        self.shell('watch a')

        path = os.path.join(self.temp_path, 'a', config.build_dir, 'a.html')
        with open(path) as file:
            self.assertEqual('hello world updated', file.read())


    def test_create_file(self):
        """Watch command should rebuild site if new file was created."""

        self.shell.before_waiting = (create_file,
                                     [os.path.join(self.temp_path, 'a', 'new.html')])
        self.shell('watch a')

        path = os.path.join(self.temp_path, 'a', config.build_dir, 'new.html')
        with open(path) as file:
            self.assertEqual('hello world', file.read())


    def test_output_option(self):
        """Watch command should read --output option and rebuild site in custom
        output directory."""

        output_path = tempfile.mkdtemp()

        self.shell.before_waiting = (modify_file,
                                     [os.path.join(self.temp_path, 'a', 'a.html')])
        self.shell('watch a --output ' + output_path)

        path = os.path.join(output_path, 'a.html')
        with open(path) as file:
            self.assertEqual('hello world updated', file.read())



class TestWatchGroupOfSites(TestCommand):
    """Tests: watch

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    def setUp(self):
        TestCommand.setUp(self)

        self.shell = CommandLineInterface()
        # For faster checking files changes.
        self.shell.set_interval(0.1)
        # After first rebuild stop command.
        self.shell.after_rebuild = self.shell.stop_waiting



    def test_modify_site(self):
        """Watch command should rebuild only modified site."""

        self.shell.before_waiting = (modify_file,
                                     [os.path.join(self.temp_path, 'a', 'a.html')])
        self.shell('watch')

        path = os.path.join(self.temp_path, 'a', config.build_dir, 'a.html')
        with open(path) as file:
            self.assertEqual('hello world updated', file.read())

        # Should not rebuild not modified sites.
        path = os.path.join(self.temp_path, 'b', config.build_dir)
        self.assertFalse(os.path.exists(path))


    def test_output_option(self):
        """Watch command should read --output option and rebuild only modified site
        in custom output directory."""

        output_path = tempfile.mkdtemp()

        self.shell.before_waiting = (modify_file,
                                     [os.path.join(self.temp_path, 'a', 'a.html')])
        self.shell('watch --output ' + output_path)

        path = os.path.join(output_path, 'a', 'a.html')
        with open(path) as file:
            self.assertEqual('hello world updated', file.read())

        # Should not rebuild not modified sites.
        path = os.path.join(output_path, 'b')
        self.assertFalse(os.path.exists(path))







    #def test_skip_output_directory(self):
    #
    #
    #    self.shell.before_waiting = self._test_create_file_in_output
    #    self.shell.after_rebuild = self.shell.stop_waiting
    #    self.shell('watch a')
    #
    #    path = os.path.join(self.temp_path, 'a', config.build_dir, 'new.html')
    #    with open(path) as file:
    #        self.assertEqual('hello world', file.read())
    #
    #def _test_create_file_in_output(self):
    #
    #    path = os.path.join(self.temp_path, 'a', config.build_dir, 'new.html')
    #    with open(path, 'w') as file:
    #        file.write('hello world')
    #
    #    self._test_modify_file()