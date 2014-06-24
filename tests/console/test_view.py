"""Tests command: view"""

import urllib.request
from stado import config
from tests.console import TestCommand


class TestView(TestCommand):
    """Command view

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    _command = 'view'

    def read_url(self, url, host, port):
        url = 'http://{}:{}/{}'.format(host, port, url)
        return urllib.request.urlopen(url).read().decode('UTF-8')

    # View module.

    def test_module(self):
        """should serve module output files [stado.py view module.py]"""

        def test():
            a = self.read_url('a.html', config.host, config.port)
            self.console.stop_waiting()

            self.assertEqual('a', a)

        self.console.before_waiting = test
        self.command('script_a.py')

    # View package.

    def test_package(self):
        """should serve package output files [stado.py view package]"""

        def test():
            a = self.read_url('a.html', config.host, config.port)
            b = self.read_url('b.html', config.host, config.port + 1)
            self.console.stop_waiting()

            self.assertEqual('a', a)
            self.assertEqual('b', b)

        self.console.before_waiting = test
        self.command('y')

    # View with no arguments.

    def test(self):
        """should serve current directory output files [stado.py view]"""

        def test():
            a = self.read_url('a.html', config.host, config.port)
            b = self.read_url('b.html', config.host, config.port + 1)
            self.console.stop_waiting()

            self.assertEqual('a', a)
            self.assertEqual('b', b)

        self.console.before_waiting = test
        self.command()

    #

    def test_host_and_port(self):
        """--host --port: should run server on custom host and port."""

        def test():
            a = self.read_url('a.html', host='127.0.0.2', port=3000)
            self.console.stop_waiting()

            self.assertEqual('a', a)

        self.console.before_waiting = test
        self.command('script_a.py --host 127.0.0.2 --port 3000')

    #

    def test_port_order(self):
        """should assign server ports in alphabetical order"""

        # In alphabetical order of script file name, for example:
        # a.py => 4000
        # b.py => 4001
        # z.py => 4002

        def test():
            a = self.read_url('foo.html', config.host, config.port)
            b = self.read_url('foo.html', config.host, config.port + 1)
            c = self.read_url('foo.html', config.host, config.port + 2)
            self.console.stop_waiting()

            self.assertEqual('a', a)
            self.assertEqual('b', b)
            self.assertEqual('c', c)

        self.console.before_waiting = test
        self.command('sort')