"""Tests command: watch"""

import os
import tempfile

from stado import config
from stado.console import Console
from tests.console import TestCommand



# Helpers.

def modify_file(path):
    """Append ' updated' data to given file."""
    with open(path, 'a') as file:
        file.write(' updated')

def create_file(path):
    """Creates new file with 'hello world' data."""
    with open(path, 'w') as file:
       file.write('hello world')

def modify_script(path):
    """Changes python script."""
    with open(path, 'w') as file:
        script = \
        (
             '\nfrom stado import Stado'
             '\napp = Stado()'
             '\n@app.before("a.html")'
             '\ndef update(page):'
             '\n    page.content = "updated"'
             '\napp.run()'
        )
        file.write(script)


class TestWatchSite(TestCommand):
    """Tests command:

        watch [site] --output

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    command = 'watch'

    def setUp(self):
        TestCommand.setUp(self)

        self.shell = Console()
        # For faster checking files changes.
        self.shell.set_interval(0.1)
        # After first rebuild stop command.
        self.shell.after_rebuild = self.shell.stop_waiting


    def test_return_true(self):
        """watch [site]: Should return True if watching ended successful."""

        self.shell.before_waiting = (modify_file,
                                     [os.path.join(self.temp_path, 'a', 'a.html')])
        self.assertTrue(self.shell(self.command + ' a'))



    def test_modify_file(self):
        """watch [site]: Watcher should react on file modifying."""

        self.shell.before_waiting = (modify_file,
                                     [os.path.join(self.temp_path, 'a', 'a.html')])
        self.shell(self.command + ' a')

        path = os.path.join(self.temp_path, 'a', config.build_dir, 'a.html')
        with open(path) as file:
            self.assertEqual('hello world updated', file.read())


    def test_create_file(self):
        """watch [site]: Watcher should react on file creating."""

        self.shell.before_waiting = (create_file,
                                     [os.path.join(self.temp_path, 'a', 'new.html')])
        self.shell(self.command + ' a')

        path = os.path.join(self.temp_path, 'a', config.build_dir, 'new.html')
        with open(path) as file:
            self.assertEqual('hello world', file.read())


    def test_modify_script(self):
        """watch [site]: Watcher should correctly re-import site.py"""

        self.shell.before_waiting = (modify_script,
                                     [os.path.join(self.temp_path, 'a', 'site.py')])
        self.shell(self.command + ' a')

        path = os.path.join(self.temp_path, 'a', config.build_dir, 'a.html')
        with open(path) as file:
            self.assertEqual('updated', file.read())


    def test_output_option(self):
        """watch [site] --output: Watcher should use custom output directory."""

        output_path = tempfile.mkdtemp()

        self.shell.before_waiting = (modify_file,
                                     [os.path.join(self.temp_path, 'a', 'a.html')])
        self.shell(self.command + ' a --output ' + output_path)

        path = os.path.join(output_path, 'a.html')
        with open(path) as file:
            self.assertEqual('hello world updated', file.read())



class TestWatchGroupOfSites(TestCommand):
    """Tests command:

        watch --output

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    def setUp(self):
        TestCommand.setUp(self)

        self.shell = Console()
        # For faster checking files changes.
        self.shell.set_interval(0.1)
        # After first rebuild stop command.
        self.shell.after_rebuild = self.shell.stop_waiting


    def test_return_true(self):
        """watch : Should return True if watching ended successful."""

        self.shell.before_waiting = (modify_file,
                                     [os.path.join(self.temp_path, 'a', 'a.html')])
        self.assertTrue(self.shell('watch'))




    def test_modify_site(self):
        """watch: Watcher should rebuild only modified site."""

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
        """watch --output: Watcher should use custom output directory."""

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
