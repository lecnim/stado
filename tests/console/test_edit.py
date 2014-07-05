"""Tests command: edit"""

import os
import urllib
from contextlib import contextmanager
from stado import config
from tests.console.test_view import TestView
from tests.console.test_watch import TestWatch
from stado.console.edit import Edit


class TestEditView(TestView):
    """Command edit - testing a development server"""

    command_class = Edit


class TestEditWatch(TestWatch):
    """Command edit - testing a watcher with a development server"""

    command_class = Edit

    @contextmanager
    def run_command(self, *args, **kwargs):
        """Starts a command with arguments, then pause it, waits for checks and
          finally stops it."""

        self.command.run(*args, stop_thread=False, **kwargs)
        self.command.pause_watcher()
        yield
        self.command.stop()

    #
    # Integration tests.
    #

    def test_server_use_updated_files(self):
        """server should use files updated by the watch command"""

        # Watch command updates files in the output of the site,
        # so a server should serve updated files.

        # Prepare files.
        self.create_file('script.py', 'from stado import build\n'
                                      'build("*.html")')
        # Action.
        with self.run_command():
            self.create_file('new.html', 'NEW')
            self.command.check()
            html = self.read_url('new.html', config.host, config.port)

        # Tests.
        self.assertEqual('NEW', html)

    def test_server_use_updated_output(self):
        """server should serve files from the correct output"""

        # The output directory was changed, so a server should change a
        # serve path.

        self.create_file('script.py', 'from stado import Site\n'
                                      'Site(output="ready").build("*.html")')
        # Action.
        with self.run_command():
            self.create_file('new.html', 'NEW')
            self.command.check()
            html = self.read_url('new.html', config.host, config.port)
            path = self.command.servers[0].path

        # Tests.
        self.assertEqual('NEW', html)
        self.assertEqual(os.path.abspath('ready'), path)

    def test_script_deleted_servers_killed(self):
        """should kill unused servers, for example when a script is removed"""

        # The script file is deleted, so it server should be killed.

        self.create_file('a.py',
                         'from stado import route\nroute("/a.html", "a")')
        self.create_file('b.py',
                         'from stado import route\nroute("/b.html", "b")')

        with self.run_command():
            self.remove_file('a.py')
            self.command.check()
            s = len(self.command.servers)

        self.assertEqual(1, s)

    def test_start_server_for_new_script(self):
        """should start a new server for each site in the new script"""

        # New script file is created, so a new server is started for each
        # new site instance.

        self.create_file('a.py',
                         'from stado import route\nroute("/a.html", "a")')

        with self.run_command():
            self.create_file('b.py',
                             'from stado import route\nroute("/b.html", "b")')
            self.command.check()
            servers = len(self.command.servers)
            html = self.read_url('b.html', config.host, config.port + 1)

        self.assertEqual(2, servers)
        self.assertEqual('b', html)

    def test_delete_site_kill_server(self):
        """should kill a server for a deleted site"""

        # Site is deleted from script file, it server must be killed.

        self.create_file('a.py', 'from stado import route, Site\n'
                                 'route("/a.html", "a")\n'
                                 'Site().route("/b.html", "b")')

        with self.run_command():
            self.modify_file('a.py', 'from stado import route\n'
                                     'route("/a.html", "a")')
            self.remove_dir(config.build_dir)
            self.command.check()
            html = self.read_url('a.html', config.host, config.port)
            servers = len(self.command.servers)

        self.assertEqual(1, servers)
        self.assertEqual('a', html)

    def test_new_site_new_server(self):
        """should start a new server for each new site in the script file"""

        # New site is add to the script file, so new server should start.

        self.create_file('a.py', 'from stado import route\n'
                                 'route("/a.html", "a")')

        with self.run_command():
            self.modify_file('a.py', 'from stado import route, Site\n'
                                     'route("/a.html", "a")\n'
                                     'Site().route("/b.html", "b")')
            self.command.check()
            html = self.read_url('b.html', config.host, config.port + 1)
            servers = len(self.command.servers)

        self.assertEqual(2, servers)
        self.assertEqual('b', html)

    def test_script_suddenly_deleted_server_killed(self):
        """should prepare for a deleting script file before rebuild"""

        # New file is created in source directory so script file is going to
        # be rerun, but before running it is suddenly deleted.

        self.create_file('script.py', 'from stado import build\n'
                                      'build("*.html")')

        with self.run_command():
            self.remove_file('script.py')
            self.create_file('a.html', 'a')
            self.command.check()
            s = len(self.command.servers)

        self.assertEqual(0, s)

    def test_serve_exception_from_modified_script(self):
        """should serve an error page if the script file raised an exception"""

        # Script file is modified and exception occurred, so server should
        # serve error page and waits for user to repair situation.

        self.create_file('a.py', 'from stado import route\n'
                                 'route("/a.html", "a")')

        with self.run_command():
            self.modify_file('a.py', 'raise ValueError("test")')
            self.command.check()

            # Requesting a file available in the output should also response
            # with an error page.
            self.assertRaises(urllib.error.HTTPError,
                              self.read_url, 'a.html', config.host, config.port)

            # Any url should response with an error page.
            try:
                self.read_url('anything', config.host, config.port)
            except urllib.error.HTTPError as e:
                self.assertEqual(500, e.code)

            self.assertEqual(1, len(self.command.servers))

            # Use repair an error - the exception is gone.

            self.modify_file('a.py', 'from stado import route\n'
                                     'route("/c.html", "c")')
            self.command.check()
            self.assertEqual('c',
                             self.read_url('c.html', config.host, config.port))

    def test_serve_exception_from_created_script(self):
        """should serve an error page if a new script file raised an exception"""

        # New script file is created and it raise the exception, so a server
        # should response with an error page.

        self.create_file('script.py', 'from stado import route\n'
                                      'route("/a.html", "a")\n'
                                      'raise ValueError("test...")')

        with self.run_command():
            self.modify_file('script.py', 'from stado import route\n'
                                          'route("/b.html", "b")\n')
            self.assertEqual(1, len(self.command.servers))
            self.command.check()

            self.assertEqual('b',
                             self.read_url('b.html', config.host, config.port))
            self.assertEqual(1, len(self.command.servers))
            self.assertEqual(2, len(self.command.file_monitor.watchers))


# Prevent running test from this classes.
del TestWatch
del TestView