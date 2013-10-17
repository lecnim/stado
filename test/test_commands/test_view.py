import os
import urllib.request

from stado import config
from commands import CommandLineInterface
from test.test_commands import TestCommand



class TestViewSite(TestCommand):
    """Tests: view [site] [host] [port]

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    def setUp(self):
        TestCommand.setUp(self)

        self.shell = CommandLineInterface()


    def test_server(self):
        """View command should correctly run server and serve files."""

        self.shell.before_waiting = self._test_server
        self.shell('view a')

    def _test_server(self):

        # Getting content from urls.
        a = urllib.request.urlopen('http://localhost:4000/a.html').read()
        self.shell.stop_waiting()

        self.assertEqual('hello world', a.decode('UTF-8'))


    def test_host_and_port(self):
        """View command should correctly run server with custom host and port."""

        self.shell.before_waiting = self._test_host_and_port
        self.shell('view a --host 127.0.0.2 --port 3000')

    def _test_host_and_port(self):

        # Getting content from urls.
        a = urllib.request.urlopen('http://127.0.0.2:3000/a.html').read()
        self.shell.stop_waiting()

        self.assertEqual('hello world', a.decode('UTF-8'))




