"""Tests command: view"""

import os
import tempfile
import shutil
import urllib.request

from commands import CommandLineInterface
from test.test_commands import TestCommand



class TestViewSite(TestCommand):
    """Tests command:

        view [site] --host --port --output

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    command = 'view'

    def setUp(self):
        TestCommand.setUp(self)

        self.shell = CommandLineInterface()


    def test_server(self):
        """view [site]: Should run server."""

        self.shell.before_waiting = self._test_server
        self.shell(self.command + ' a')

    def _test_server(self):

        # Getting content from urls.
        a = urllib.request.urlopen('http://localhost:4000/a.html').read()
        self.shell.stop_waiting()

        self.assertEqual('hello world', a.decode('UTF-8'))


    def test_host_and_port(self):
        """view [site] --host --port: Should run server on custom host and port."""

        self.shell.before_waiting = self._test_host_and_port
        self.shell(self.command + ' a --host 127.0.0.2 --port 3000')

    def _test_host_and_port(self):

        # Getting content from urls.
        a = urllib.request.urlopen('http://127.0.0.2:3000/a.html').read()
        self.shell.stop_waiting()

        self.assertEqual('hello world', a.decode('UTF-8'))


    def test_output_option(self):
        """view [site] --output: Should run server in custom output directory."""

        output_path = tempfile.mkdtemp()

        self.shell.before_waiting = self._test_output_option
        self.shell(self.command + ' a --output ' + output_path)

        # Should build site in output directory.
        path = os.path.join(output_path, 'a.html')
        self.assertTrue(os.path.exists(path))

        shutil.rmtree(output_path)

    def _test_output_option(self):

        # Getting content from urls.
        a = urllib.request.urlopen('http://localhost:4000/a.html').read()
        self.shell.stop_waiting()

        self.assertEqual('hello world', a.decode('UTF-8'))
