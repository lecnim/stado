"""Tests command: edit"""

import os
from contextlib import contextmanager
from stado import config
from tests.console.test_view import TestView
from tests.console.test_watch import TestWatch
from stado.console.edit import Edit


class TestEditView(TestView):
    """Command edit (testing development server)"""

    command_class = Edit


class TestEditWatch(TestWatch):
    """Command edit (testing watcher with development server)"""

    command_class = Edit

    @contextmanager
    def run_command(self, *args, **kwargs):
        """Starts a command with arguments, then pause it, waits for checks and
          finally stops command."""

        self.command.run(*args, stop_thread=False, **kwargs)
        self.command.watch_cmd.pause()
        yield
        self.command.stop()

    def test_server_use_updated_files(self):
        """server should use files updated by watcher"""

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

    def test_kill_unused_server(self):
        """should kill unused servers (for example when script is removed)"""

        # $ stado.py watch

        self.create_file('a.py',
                         'from stado import route\nroute("/a.html", "a")')
        self.create_file('b.py',
                         'from stado import route\nroute("/b.html", "b")')

        with self.run_command():
            self.remove_dir(config.build_dir)
            self.remove_file('a.py')
            self.command.check()
            s = len(self.command.servers)

        self.assertEqual(1, s)

    def test_start_server_for_new_site(self):

       self.create_file('a.py',
                        'from stado import route\nroute("/a.html", "a")')

       with self.run_command():
           self.create_file('b.py',
                            'from stado import route\nroute("/b.html", "b")')
           self.command.check()
           s = len(self.command.servers)

       self.assertEqual(2, s)



# Prevent running test from this classes.
del TestWatch
del TestView