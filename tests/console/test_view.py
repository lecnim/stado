"""Tests command: view"""

import urllib.request
from stado import config
from tests.console import TestCommandNew
from stado.console import View


class TestView(TestCommandNew):
    """Command view

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    command_class = View

    def read_url(self, url, host, port):
        url = 'http://{}:{}/{}'.format(host, port, url)
        return urllib.request.urlopen(url).read().decode('UTF-8')

    # View module.

    def test_serve_module_output(self):
        """should serve module output files"""

        # Prepare files.
        self.create_file('script.py', 'from stado import route\n'
                                      'route("/a.html", "a")')

        # Action.
        self.command.run('script.py', stop_thread=False)
        a = self.read_url('a.html', config.host, config.port)
        self.command.stop()

        # Test.
        self.assertEqual('a', a)

    def test_serve_package_output(self):
        """should serve package output files"""

        # Prepare files.
        self.create_file('x/a.py', 'from stado import route\n'
                                   'route("/a.html", "a")')
        self.create_file('x/b.py', 'from stado import route\n'
                                   'route("/b.html", "b")')
        # Action.
        self.command.run('x', stop_thread=False)
        a = self.read_url('a.html', config.host, config.port)
        b = self.read_url('b.html', config.host, config.port + 1)
        self.command.stop()

        # Tests.
        self.assertEqual('a', a)
        self.assertEqual('b', b)

        # No arguments:

        # Prepare files.
        self.create_file('a.py', 'from stado import route\n'
                                 'route("/a.html", "a")')
        self.create_file('b.py', 'from stado import route\n'
                                 'route("/b.html", "b")')
        # Actions.
        self.command.run(stop_thread=False)
        a = self.read_url('a.html', config.host, config.port)
        b = self.read_url('b.html', config.host, config.port + 1)
        self.command.stop()

        # Tests.
        self.assertEqual('a', a)
        self.assertEqual('b', b)

    #

    def test_host_and_port(self):
        """can run server on custom host and port."""

        # Prepare files.
        self.create_file('script.py', 'from stado import route\n'
                                      'route("/a.html", "a")')
        # Actions.
        self.command.run('script.py', host='127.0.0.2', port=3000,
                         stop_thread=False)
        a = self.read_url('a.html', host='127.0.0.2', port=3000)
        self.command.stop()

        # Tests.
        self.assertEqual('a', a)

    #

    def test_port_order(self):
        """should assign server ports in alphabetical order"""

        # In alphabetical order of script file name, for example:
        # a.py => 4000
        # b.py => 4001
        # z.py => 4002

        self.create_file('a.py',
                         'from stado import Site\n'
                         'Site(output="a").route("/foo.html", "a")')
        self.create_file('b.py',
                         'from stado import Site\n'
                         'Site(output="b").route("/foo.html", "b")')
        self.create_file('z.py',
                         'from stado import Site\n'
                         'Site(output="z").route("/foo.html", "z")')

        # Actions.
        self.command.run(stop_thread=False)
        a = self.read_url('foo.html', config.host, config.port)
        b = self.read_url('foo.html', config.host, config.port + 1)
        c = self.read_url('foo.html', config.host, config.port + 2)
        self.command.stop()

        # Tests.
        self.assertEqual('a', a)
        self.assertEqual('b', b)
        self.assertEqual('z', c)