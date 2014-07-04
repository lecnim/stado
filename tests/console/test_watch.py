"""Tests command: watch"""

import os
from contextlib import contextmanager
from stado import config
from stado.console import Console
from stado.console.watch import Watch
from tests.console import TestCommandNew


class TestWatch(TestCommandNew):
    """A watch command"""

    command_class = Watch

    @contextmanager
    def run_command(self, *args, **kwargs):
        """Starts a command with arguments, then pause it, waits for checks and
          finally stops command."""

        self.command.run(*args, stop_thread=False, **kwargs)
        self.command.pause()
        yield
        self.command.stop()

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

        # Tests:
        self.assertEqual('UPDATE', self.read_file(config.build_dir + '/a.html'))


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

        self.assertEqual('UPDATE',
                         self.read_file('x/' + config.build_dir + '/foo.html'))
        self.assertEqual('UPDATE', self.read_file('x/output_b/foo.html'))


        # $ stado.py watch

        # TODO: Add another python script to check if every script is executed.

        with self.run_command(path=None):
            self.modify_file('a.html', data='HELLO')
            self.command.check()

        # Tests:
        self.assertEqual('HELLO', self.read_file(config.build_dir + '/a.html'))

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

        # Tests:
        self.assertEqual('NEW', self.read_file(config.build_dir + '/new.html'))


        # $ stado.py watch package

        self.create_file('x/script.py',
                         'from stado import build\nbuild("*.html")')

        with self.run_command(path='x'):
            self.create_file('x/new.html', 'NEW')
            self.command.check()

        self.assertEqual('NEW',
                         self.read_file('x/' + config.build_dir + '/new.html'))

        # $ stado.py watch

        self.create_file('script.py',
                         'from stado import build\nbuild("*.html")')

        with self.run_command(path=None):
            self.create_file('another.html', 'FOOBAR')
            self.command.check()

        self.assertEqual('FOOBAR',
                         self.read_file(config.build_dir + '/another.html'))

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

            # self.assertEqual(1, len(self.command.file_monitor.watchers))

        a = os.path.join(config.build_dir, 'a.html')
        b = os.path.join(config.build_dir, 'b.html')
        self.assertFalse(os.path.exists(a))
        self.assertTrue(os.path.exists(b))

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
            self.assertEqual(1, len(self.command.file_monitor.watchers))

            w = list(self.command.file_monitor.watchers)[0]
            self.assertEqual(self.temp_path, w.path)
            self.assertFalse(w.is_recursive)

    #
    # Console.
    #

    def test_console(self):
        """should works with console"""

        # Prepare files.
        self.create_file('script.py',
                         'from stado import route\nroute("/a.html", "a")')

        def on_event(event):
            if event.cmd.name == 'watch' and event.type == 'on_run':
                console.stop()

        console = Console()
        console.events.subscribe(on_event)
        console(self.command_class.name)

        self.assertEqual('a', self.read_file(config.build_dir + '/a.html'))