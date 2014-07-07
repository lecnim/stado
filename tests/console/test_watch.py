"""Tests command: watch"""

import os
import threading
from contextlib import contextmanager

from stado import config
from stado.console import Console, CommandError
from stado.console.cmds.watch import Watch
from stado.core.site import Site
from tests.console import TestCommand


class TestWatch(TestCommand):
    """A watch command"""

    command_class = Watch

    @contextmanager
    def run_command(self, *args, **kwargs):
        """Starts a command with arguments, then pause it, waits for checks and
          finally stops command."""

        self.command.run(*args, stop_thread=False, **kwargs)
        self.command.pause()
        yield
        self.command.cancel()

    #

    def test_check_interval(self):
        config.watch_interval = 4
        x = Watch()
        self.assertEqual(4, x.file_monitor.check_interval)

    #
    # Modifying site source files.
    #

    def test_modify_file(self):
        """should monitor modified files"""

        # $ stado.py watch module.py

        # Prepare files:
        self.create_file('script.py', 'from stado import build\n'
                                      'build("a.html")')
        self.create_file('a.html', '')

        # Steps:
        with self.run_command(path='script.py'):
            self.modify_file('a.html')
            self.command.check()
            w = len(self.command.file_monitor.watchers)

        # Tests:
        self.assertEqual('UPDATE', self.read_file(config.build_dir + '/a.html'))
        self.assertEqual(2, w)


        # $ stado.py watch package

        self.create_file('x/a.py',
                         'from stado import build\nbuild("foo.html")')
        self.create_file('x/b.py',
                         'from stado import Site\n'
                         'Site(output="output_b").build("*.html")')
        self.create_file('x/foo.html', '')

        with self.run_command(path='x'):
            self.modify_file('x/foo.html')
            self.command.check()
            w = len(self.command.file_monitor.watchers)

        self.assertEqual('UPDATE',
                         self.read_file('x/' + config.build_dir + '/foo.html'))
        self.assertEqual('UPDATE', self.read_file('x/output_b/foo.html'))
        self.assertEqual(3, w)

        # $ stado.py watch

        self.create_file('another.py', 'from stado import route\n'
                                       'route("/b.html", "WORLD")')

        with self.run_command(path=None):
            self.modify_file('a.html', data='HELLO')
            self.command.check()
            w = len(self.command.file_monitor.watchers)

        # Tests:
        self.assertEqual('HELLO', self.read_file(config.build_dir + '/a.html'))
        self.assertEqual('WORLD', self.read_file(config.build_dir + '/b.html'))
        self.assertEqual(3, w)

    #
    # Creating new files.
    #

    def test_create_file(self):
        """should monitor created files"""

        # $ stado.py watch module.py

        # Prepare files:
        self.create_file('script.py',
                         'from stado import build\nbuild("*.html")')

        # Steps:
        with self.run_command(path='script.py'):
            self.create_file('new.html', 'NEW')
            self.command.check()
            w = len(self.command.file_monitor.watchers)

        # Tests:
        self.assertEqual('NEW', self.read_file(config.build_dir + '/new.html'))
        self.assertEqual(2, w)

        # $ stado.py watch package

        self.create_file('x/script.py',
                         'from stado import build\nbuild("*.html")')

        with self.run_command(path='x'):
            self.create_file('x/new.html', 'NEW')
            self.command.check()
            w = len(self.command.file_monitor.watchers)

        self.assertEqual('NEW',
                         self.read_file('x/' + config.build_dir + '/new.html'))
        self.assertEqual(2, w)

        # $ stado.py watch

        self.create_file('script.py',
                         'from stado import build\nbuild("*.html")')

        with self.run_command(path=None):
            self.create_file('another.html', 'FOOBAR')
            self.command.check()
            w = len(self.command.file_monitor.watchers)

        self.assertEqual('FOOBAR',
                         self.read_file(config.build_dir + '/another.html'))
        self.assertEqual(2, w)

    #
    # Removing files.
    #

    def test_remove_file(self):
        """should monitor on deleted files"""

        # $ stado.py watch module.py

        # Prepare files:
        self.create_file('script.py',
                         'from stado import build\nbuild("*.html")')
        self.create_file('a.html', 'a')
        self.create_file('b.html', 'b')

        # Steps:
        with self.run_command(path='script.py'):
            # Output must be empty!
            self.remove_dir(config.build_dir)
            self.remove_file('a.html')
            self.command.check()

        # Tests:
        a = os.path.join(config.build_dir, 'a.html')
        b = os.path.join(config.build_dir, 'b.html')
        self.assertFalse(os.path.exists(a))
        self.assertTrue(os.path.exists(b))


        # $ stado.py watch package

        self.create_file('x/script.py',
                         'from stado import build\nbuild("*.html")')
        self.create_file('x/a.html', '')
        self.create_file('x/b.html', '')

        with self.run_command(path='x'):
            self.remove_dir('x/' + config.build_dir)
            self.remove_file('x/a.html')
            self.command.check()

        a = os.path.join('x', config.build_dir, 'a.html')
        b = os.path.join('x', config.build_dir, 'b.html')
        self.assertFalse(os.path.exists(a))
        self.assertTrue(os.path.exists(b))

    #
    # Modifying python script file.
    #

    def test_modify_script(self):
        """should re-import modified python script"""

        # $ stado.py watch module.py

        # Prepare files:
        self.create_file('script.py',
                         'from stado import build\nbuild("a.html")')
        self.create_file('a.html', '')
        self.create_file('foo.html', '')

        # Steps:
        with self.run_command(path='script.py'):
            self.modify_file('script.py',
                             'from stado import build\nbuild("foo.html")')
            self.command.check()

        # Tests:
        a = os.path.join(config.build_dir, 'a.html')
        b = os.path.join(config.build_dir, 'foo.html')
        self.assertTrue(os.path.exists(a))
        self.assertTrue(os.path.exists(b))


        # $ stado.py watch

        self.create_file('script.py',
                         'from stado import build\nbuild("a.html")')
        self.create_file('script_2.py',
                         'from stado import Site\nSite().build("a.html")')
        self.create_file('c.html', '')

        with self.run_command(path=None):
            self.modify_file('script.py',
                             'from stado import build\nbuild("foo.html")')
            self.modify_file('script_2.py',
                             'from stado import build\nbuild("c.html")')
            self.command.check()

        a = os.path.join(config.build_dir, 'a.html')
        b = os.path.join(config.build_dir, 'foo.html')
        c = os.path.join(config.build_dir, 'c.html')
        self.assertTrue(os.path.exists(a))
        self.assertTrue(os.path.exists(b))
        self.assertTrue(os.path.exists(c))


        # $ stado.py watch package

        self.create_file('x/a.py',
                         'from stado import build\nbuild("a.html")')
        self.create_file('x/b.py',
                         'from stado import Site\nSite().build("a.html")')
        self.create_file('x/a.html', 'a')
        self.create_file('x/b.html', 'a')
        self.create_file('x/c.html', 'a')

        with self.run_command(path='x'):
            self.modify_file('x/a.py',
                             'from stado import build\nbuild("b.html")')
            self.modify_file('x/b.py',
                             'from stado import build\nbuild("c.html")')
            self.command.check()

        a = os.path.join('x', config.build_dir, 'a.html')
        b = os.path.join('x', config.build_dir, 'b.html')
        c = os.path.join('x', config.build_dir, 'c.html')
        self.assertTrue(os.path.exists(a))
        self.assertTrue(os.path.exists(b))
        self.assertTrue(os.path.exists(c))

    def test_modify_script_with_custom_source(self):

        self.create_file('script.py',
                         'from stado import Site\n'
                         'Site("src").build("hello.html")')
        self.create_file('src/hello.html', 'hello')
        self.create_file('src/another.html', 'another')

        with self.run_command('script.py'):
            self.modify_file('script.py',
                             'from stado import Site\n'
                             'Site("src").build("another.html")')
            self.command.check()

        hello = os.path.join('src', config.build_dir, 'hello.html')
        another = os.path.join('src', config.build_dir, 'another.html')
        self.assertTrue(os.path.exists(hello))
        self.assertTrue(os.path.exists(another))

    #
    # Adding new python scripts.
    #

    def test_new_site_instance_in_module(self):
        """should build every new site instance in module"""

        # Prepare files:
        self.create_file('script.py',
                         'from stado import route\nroute("/a.html", "a")')

        # Steps:
        with self.run_command(path='script.py'):
            self.modify_file('script.py',
                             'from stado import route, Site\n'
                             'route("/a.html", "a")\n'
                             'Site().route("/b.html","b")')
            self.command.check()

        # Tests:
        a = os.path.join(config.build_dir, 'a.html')
        b = os.path.join(config.build_dir, 'b.html')
        self.assertTrue(os.path.exists(a))
        self.assertTrue(os.path.exists(b))
        self.assertEqual('a', self.read_file(a))
        self.assertEqual('b', self.read_file(b))

    def test_new_script_in_package(self):
        """should build every new script in package"""

        self.create_file('script.py',
                         'from stado import route\nroute("/a.html", "a")')

        with self.run_command(path=None):
            self.create_file('new.py',
                             'from stado import route\nroute("/b.html", "b")')
            self.command.check()

        a = os.path.join(config.build_dir, 'a.html')
        b = os.path.join(config.build_dir, 'b.html')
        self.assertTrue(os.path.exists(a))
        self.assertTrue(os.path.exists(b))
        self.assertEqual('a', self.read_file(a))
        self.assertEqual('b', self.read_file(b))

    #
    # Removing python scripts.
    #

    def test_remove_script(self):
        """should not monitor already deleted scripts"""

        # $ stado.py watch

        self.create_file('a.py',
                         'from stado import route\nroute("/a.html", "a")')
        self.create_file('b.py',
                         'from stado import route\nroute("/b.html", "b")')

        with self.run_command(path=None):
            self.remove_dir(config.build_dir)
            self.remove_file('a.py')
            self.command.check()
            w = len(self.command.file_monitor.watchers)

        a = os.path.join(config.build_dir, 'a.html')
        b = os.path.join(config.build_dir, 'b.html')
        self.assertFalse(os.path.exists(a))
        self.assertTrue(os.path.exists(b))
        self.assertEqual(2, w)

    # TODO: Removing module which is currently run.

    #
    # Rebuilding.
    #

    def test_rebuild(self):
        """should correctly rebuilds site multiple times"""

        self.create_file('script.py',
                         'from stado import build\nbuild("*.html")')

        with self.run_command(path=None):
            self.create_file('new.html')
            self.command.check()
            self.create_file('another.html')
            self.command.check()

        a = os.path.join(config.build_dir, 'new.html')
        b = os.path.join(config.build_dir, 'another.html')
        self.assertTrue(os.path.exists(a))
        self.assertTrue(os.path.exists(b))

    #
    # Exceptions.
    #

    def test_path_not_found(self):
        """should raise an exception when a path is not found"""

        self.assertRaises(CommandError, self.command.run,
                          path='path/not/found',
                          stop_thread=False)

        # Should stop servers, clean etc...
        self.assertFalse(self.command.is_running)
        self.assertEqual(0, len(self.command.file_monitor.watchers))
        self.assertEqual(0, len(Site._tracker.records))

    def test_exception_in_modified_script(self):
        """should still work if a modified file raise an exception"""

        # Script file is modified and exception occurred. Watcher should
        # wait until user repair error.

        self.create_file('a.py', 'from stado import route\n'
                                 'route("/a.html", "a")')

        with self.run_command():
            self.modify_file('a.py', 'raise ValueError("do not worry'
                                     ' - this is test")')
            self.command.check()

            self.assertEqual(2, len(self.command.file_monitor.watchers))

            # Use repair an error - the exception is gone.

            self.modify_file('a.py', 'from stado import route\n'
                                     'route("/c.html", "c")')
            self.command.check()
            self.assertEqual('c', self.read_file(config.build_dir + '/c.html'))

    def test_run_script_exception(self):
        """should still work if run raise an exception from the script file"""

        # Command is run but one of script files raise an exception.
        # It should wait unit error is repaired.

        self.create_file('script.py', 'from stado import route\n'
                                      'route("/a.html", "a")\n'
                                      'raise ValueError("do not worry'
                                     ' - this is test")')

        with self.run_command():
            self.modify_file('script.py', 'from stado import route\n'
                                          'route("/b.html", "b")\n')
            self.assertEqual(2, len(self.command.file_monitor.watchers))
            self.command.check()
            self.assertEqual('b', self.read_file(config.build_dir + '/b.html'))
            self.assertEqual(2, len(self.command.file_monitor.watchers))

    #
    # Other.
    #

    def test_watchers(self):
        """should creates correct watchers instances"""

        # $ stado.py watch module.py

        # Prepare files:
        self.create_file('script.py', 'from stado import build\n'
                                      'build("a.html")')
        self.create_file('a.html', '')

        # Steps and tests:
        with self.run_command(path='script.py'):

            # Only one watcher, package watcher is not used in this situation.
            self.assertEqual(2, len(self.command.file_monitor.watchers))

            w = list(self.command.file_monitor.watchers)[0]
            self.assertEqual(self.temp_path, w.path)
            self.assertFalse(w.is_recursive)

    #
    # Console.
    #

    def test_console_integration(self):
        """should works with console"""

        # Prepare files.
        self.create_file('script.py',
                         'from stado import route\nroute("/a.html", "a")')

        def on_event(event):
            if event.cmd.name == self.command_class.name \
               and event.type == 'on_wait':
                console.stop()

        console = Console()
        console.events.subscribe(on_event)
        console(self.command_class.name)

        self.assertEqual('a', self.read_file(config.build_dir + '/a.html'))

    def test_console_path_not_found(self):
        """console should return False if path is not found"""

        console = Console()
        self.assertFalse(console(self.command_class.name + ' not_found.py'))

    def test_console_wait_on_empty_file_or_directory(self):
        """should wait even if the path is empty directory or empty file"""

        wait = False

        def on_event(event):
            if event.cmd.name == self.command_class.name \
               and event.type == 'on_wait':

                nonlocal wait
                wait = True
                threading.Timer(0.25, console.stop).start()

        console = Console()
        console.events.subscribe(on_event)

        # Empty directory.
        console(self.command_class.name)
        self.assertTrue(wait)

        # Empty file.
        wait = False
        self.create_file('empty.py', '')
        console(self.command_class.name + ' empty.py')
        self.assertTrue(wait)