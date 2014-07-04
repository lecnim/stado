"""Tests command: watch"""

import os
import shutil
import time
import unittest
from stado.utils import copytree
import tempfile
import threading
from stado import config
from stado import Console
from stado.console.watch import Watch
from tests.console import TestCommand, TestCommandNew

from contextlib import contextmanager


class TestNEWNEwWatch(TestCommandNew):
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
    # Console support.
    #

    # TODO

    # def test_module_modify_file(self):
    #     """watcher should react on file modifying [stado.py watch module.py]"""
    #
    #     console = Console()
    #
    #     # Prepare files:
    #     self.create_file('script.py',
    #                      'from stado import build\nbuild("a.html")')
    #     self.create_file('a.html', '')
    #
    #     # Assumptions:
    #
    #     def event(path):
    #         if path == os.path.abspath('script.py'):
    #             console.stop_waiting()
    #
    #     # Action:
    #     console.on_rebuild = event
    #
    #     console.on_run_watch = event
    #     # console(self.command_class.name + ' script.py')
    #     thread = threading.Thread(target=console, args=(self.command_class.name + ' script.py',))
    #
    #     self.modify_file('a.html')
    #     self.wait()
    #
    #     # x = lambda: 'UPDATE' == self.read_file(config.build_dir + '/a.html')
    #     # self.stop_if(x)
    #
    #     # Tests:
    #     self.assertEqual('UPDATE', self.read_file(config.build_dir + '/a.html'))
    #
    #
    #
    #     console.watch.event_run.wait()
    #
    #     event_run.wait()
    #     console.pause()
    #     self.modify_file('a.html')
    #     console.resume()
    #     event_update.wait()
    #     console.stop()







#
# class TestNewWatch(TestCommand):
#
#     _command = 'watch'
#
#     def setUp(self):
#
#         # Path pointing to current working directory.
#         self.cwd = os.getcwd()
#
#         # Path to commands test directory.
#         self.path = os.path.dirname(__file__)
#
#         # Path to temporary directory with sites.
#         self.temp_path = tempfile.mkdtemp()
#         # copytree(os.path.join(self.path, self.data_path), self.temp_path)
#
#         # Set current working directory to temporary directory with sites.
#         os.chdir(self.temp_path)
#
#         self.console = Console()
#
#         # For faster checking files changes.
#         self.console.set_interval(0.1)
#
#     def tearDown(self):
#
#         # Go to previous working directory and clear files.
#         os.chdir(self.cwd)
#         shutil.rmtree(self.temp_path)
#     #
#     # def setUp(self):
#     #     TestCommand.setUp(self)
#     #
#     #
#
#     def run_command(self, args=''):
#         """Execute console command with given arguments string."""
#
#         ok = threading.Event()
#
#         def event(command):
#             nonlocal ok
#             if command.name == self._command:
#                 ok.set()
#
#         self.console.on_started = event
#
#         self.thread = threading.Thread(target=self.console,
#                                        args=(self._command + ' ' + args,))
#         self.thread.start()
#
#
#         ok.wait()
#         # return self.console(self._command + ' ' + args)
#
#     def wait(self):
#         self.thread.join()
#
#
#     def modify_file(self, path, data='UPDATE'):
#
#         with open(os.path.join(*path.split('/')), 'w') as file:
#             file.write(data)
#
#     def read_file(self, path):
#         """Returns data from given path, relative to current temp path."""
#
#         fp = os.path.join(self.temp_path, *path.split('/'))
#         self.assertTrue(os.path.exists(fp),
#                         msg='path not found: ' + fp)
#
#         with open(fp) as file:
#             return file.read()
#
#     def create_file(self, path, data):
#
#         path = os.path.abspath(os.path.join(*path.split('/')))
#         dir_path = os.path.dirname(path)
#
#         if not os.path.exists(dir_path):
#             os.makedirs(dir_path)
#
#
#         with open(path, 'w') as file:
#             file.write(data)
#
#     def create_dir(self, path):
#         os.makedirs(os.path.join(*path.split('/')))
#
#
#     def remove_file(self, path):
#         """BE CAREFUL! Removes given file."""
#         os.remove(os.path.join(self.temp_path, os.path.join(*path.split('/'))))
#
#     def remove_dir(self, path):
#         """BE CAREFUL! Removes directory recursively."""
#         p = os.path.join(os.path.join(self.temp_path, os.path.join(*path.split('/'))))
#         shutil.rmtree(p)
#
#
#     def stop_on_rebuild(self, *paths):
#
#         paths = [os.path.abspath(os.path.join(*i.split('/'))) for i in paths]
#
#         def event(rebuild_path):
#             nonlocal paths
#             if rebuild_path in paths:
#                 paths.remove(rebuild_path)
#                 if not paths:
#                     self.console.stop_waiting()
#
#         self.console.on_rebuild = event
#
#
#     def stop_on_create_script(self, *paths):
#
#         paths = [os.path.abspath(os.path.join(*i.split('/'))) for i in paths]
#
#         def event(rebuild_path):
#             nonlocal paths
#             if rebuild_path in paths:
#                 paths.remove(rebuild_path)
#                 if not paths:
#                     self.console.stop_waiting()
#
#         self.console.on_create_script = event
#
#
#     def stop_if(self, target, args=(), kwargs={}, timeout=None):
#
#
#
#         while not target(*args, **kwargs):
#             time.sleep(0.1)
#
#         self.console.stop_waiting()
#         self.thread.join()
#
#     # Modifying source files.
#
#     def test_module_modify_file(self):
#         """watcher should react on file modifying [stado.py watch module.py]"""
#
#         # Prepare files:
#         self.create_file('script.py',
#                          'from stado import build\nbuild("a.html")')
#         self.create_file('a.html', '')
#
#         # Assumptions:
#         self.stop_on_rebuild('script.py')
#
#         # Action:
#         self.run_command(args='script.py')
#         self.modify_file('a.html')
#         self.wait()
#
#         # x = lambda: 'UPDATE' == self.read_file(config.build_dir + '/a.html')
#         # self.stop_if(x)
#
#         # Tests:
#         self.assertEqual('UPDATE', self.read_file(config.build_dir + '/a.html'))
#
#     def test_package_modify_file(self):
#         """watcher should react on file modifying [stado.py watch package]"""
#
#         # Prepare files:
#         self.create_file('x/a.py',
#                          'from stado import build\nbuild("foo.html")')
#         self.create_file('x/b.py',
#                          'from stado import Site\n'
#                          'Site(output="output_b").build("*.html")')
#         self.create_file('x/foo.html', '')
#
#         # Assumptions:
#         self.stop_on_rebuild('x/a.py', 'x/b.py')
#
#         # Action:
#         self.run_command(args='x')
#         self.modify_file('x/foo.html')
#         self.wait()
#
#         # Tests:
#         self.assertEqual('UPDATE',
#                          self.read_file('x/' + config.build_dir + '/foo.html'))
#         self.assertEqual('UPDATE', self.read_file('x/output_b/foo.html'))
#
#     def test_modify_file(self):
#         """watcher should react on file modifying [stado.py watch]"""
#
#         # Prepare files:
#         self.create_file('script.py',
#                          'from stado import build\nbuild("a.html")')
#         self.create_file('a.html', '')
#
#         # Assumptions:
#         self.stop_on_rebuild('script.py')
#
#         # Action:
#         self.run_command(args='')
#         self.modify_file('a.html')
#         self.wait()
#
#         # Tests:
#         self.assertEqual('UPDATE', self.read_file(config.build_dir + '/a.html'))
#
#     # Creating new files.
#
#     def test_module_create_file(self):
#         """watcher should react on file creating [stado.py watch module.py]"""
#
#         # Prepare files:
#         self.create_file('script.py',
#                          'from stado import build\nbuild("*.html")')
#
#         # Assumptions:
#         self.stop_on_rebuild('script.py')
#
#         # Action:
#         self.run_command(args='script.py')
#         self.create_file('new.html', 'NEW')
#         self.wait()
#
#         # Tests:
#         self.assertEqual('NEW', self.read_file(config.build_dir + '/new.html'))
#
#     def test_package_create_file(self):
#         """watcher should react on file creating [stado.py watch package]"""
#
#         # Prepare files:
#         self.create_file('x/script.py',
#                          'from stado import build\nbuild("*.html")')
#
#         # Assumptions:
#         self.stop_on_rebuild('x/script.py')
#         # self.stop_if_file_exists()
#
#         # Action:
#         self.run_command(args='x')
#         self.create_file('x/new.html', 'NEW')
#         self.wait()
#
#         # Tests:
#         self.assertEqual('NEW',
#                          self.read_file('x/' + config.build_dir + '/new.html'))
#
#     def test_create_file(self):
#         """watcher should react on file creating [stado.py watch]"""
#
#         # Prepare files:
#         self.create_file('script.py',
#                          'from stado import build\nbuild("*.html")')
#
#         # Assumptions:
#         self.stop_on_rebuild('script.py')
#
#         # Action:
#         self.run_command(args='')
#         self.create_file('new.html', 'NEW')
#         self.wait()
#
#         # Tests:
#         self.assertEqual('NEW',
#                          self.read_file(config.build_dir + '/new.html'))
#
#     # Removing files.
#
#     def test_module_remove_file(self):
#         """watcher should react on file removing [stado.py watch module.py]"""
#
#         # Prepare files:
#         self.create_file('script.py',
#                          'from stado import build\nbuild("*.html")')
#         self.create_file('a.html', '')
#         self.create_file('b.html', '')
#
#         # Assumptions:
#         self.stop_on_rebuild('script.py')
#
#         # Action:
#         self.run_command(args='script.py')
#         self.remove_dir(config.build_dir)
#         self.remove_file('a.html')
#         self.wait()
#
#         # Tests:
#         a = os.path.join(config.build_dir, 'a.html')
#         b = os.path.join(config.build_dir, 'b.html')
#         self.assertFalse(os.path.exists(a))
#         self.assertTrue(os.path.exists(b))
#
#     def test_package_remove_file(self):
#         """watcher should react on file removing [stado.py watch package]"""
#
#         # Prepare files:
#         self.create_file('x/script.py',
#                          'from stado import build\nbuild("*.html")')
#         self.create_file('x/a.html', '')
#         self.create_file('x/b.html', '')
#
#         # Assumptions:
#         self.stop_on_rebuild('x/script.py')
#
#         # Action:
#         self.run_command(args='x')
#         self.remove_dir('x/' + config.build_dir)
#         self.remove_file('x/a.html')
#         self.wait()
#
#         # Tests:
#         a = os.path.join('x', config.build_dir, 'a.html')
#         b = os.path.join('x', config.build_dir, 'b.html')
#         self.assertFalse(os.path.exists(a))
#         self.assertTrue(os.path.exists(b))
#
#     # Modifying python script file.
#
#     def test_module_modify_script(self):
#         """watcher should re-import modified script [stado.py watch module.py]"""
#
#         # Prepare files:
#         self.create_file('script.py',
#                          'from stado import build\nbuild("a.html")')
#         self.create_file('a.html', '')
#         self.create_file('b.html', '')
#
#         # Assumptions:
#         self.stop_on_rebuild('script.py')
#
#         # Action:
#         self.run_command(args='script.py')
#         self.modify_file('script.py',
#                          'from stado import build\nbuild("b.html")')
#         self.wait()
#         # self.stop_if(os.path.exists, path=os.path.join(config.build_dir, 'b.html'))
#
#         # Tests:
#         a = os.path.join(config.build_dir, 'a.html')
#         b = os.path.join(config.build_dir, 'b.html')
#         self.assertTrue(os.path.exists(a))
#         self.assertTrue(os.path.exists(b))
#
#     def test_package_modify_script(self):
#         """watcher should re-import modified script [stado.py watch package]"""
#
#         # Prepare files:
#         self.create_file('x/a.py',
#                          'from stado import build\nbuild("a.html")')
#         self.create_file('x/b.py',
#                          'from stado import Site\nSite().build("a.html")')
#         self.create_file('x/a.html', 'a')
#         self.create_file('x/b.html', 'a')
#         self.create_file('x/c.html', 'a')
#
#         # Assumptions:
#         self.stop_on_rebuild('x/a.py', 'x/b.py')
#
#         # Action:
#         self.run_command(args='x')
#         # self.console.pause()
#         self.modify_file('x/a.py', 'from stado import build\nbuild("b.html")')
#         self.modify_file('x/b.py', 'from stado import build\nbuild("c.html")')
#         # self.console.resume()
#         self.wait()
#
#         # Tests:
#         a = os.path.join('x', config.build_dir, 'a.html')
#         b = os.path.join('x', config.build_dir, 'b.html')
#         c = os.path.join('x', config.build_dir, 'c.html')
#         self.assertTrue(os.path.exists(a))
#         self.assertTrue(os.path.exists(b))
#         self.assertTrue(os.path.exists(c))
#
#     def test_modify_script(self):
#         """watcher should re-import modified script [stado.py watch]"""
#
#         # Prepare files:
#         self.create_file('a.py',
#                          'from stado import build\nbuild("a.html")')
#         self.create_file('b.py',
#                          'from stado import Site\nSite().build("a.html")')
#         self.create_file('a.html', '')
#         self.create_file('b.html', '')
#         self.create_file('c.html', '')
#
#         # Assumptions:
#         self.stop_on_rebuild('a.py', 'b.py')
#
#         # Action:
#         self.run_command(args='')
#         self.modify_file('a.py', 'from stado import build\nbuild("b.html")')
#         self.modify_file('b.py', 'from stado import build\nbuild("c.html")')
#         self.wait()
#
#         # Tests:
#         a = os.path.join(config.build_dir, 'a.html')
#         b = os.path.join(config.build_dir, 'b.html')
#         c = os.path.join(config.build_dir, 'c.html')
#         self.assertTrue(os.path.exists(a))
#         self.assertTrue(os.path.exists(b))
#         self.assertTrue(os.path.exists(c))
#
#     # Adding new python scripts.
#
#     def test_module_create_site(self):
#         """watcher should build every new site instance in module"""
#
#
#         # Prepare files:
#         self.create_file('script.py',
#                          'from stado import route\nroute("/a.html", "a")')
#
#         # Assumptions:
#         self.stop_on_rebuild('script.py')
#
#         # Action:
#         self.run_command(args='script.py')
#         self.modify_file('script.py',
#                          'from stado import route, Site\n'
#                          'route("/a.html", "a")\n'
#                          'Site().route("/b.html","b")')
#         self.wait()
#
#         # Tests:
#         a = os.path.join(config.build_dir, 'a.html')
#         b = os.path.join(config.build_dir, 'b.html')
#         self.assertTrue(os.path.exists(a))
#         self.assertTrue(os.path.exists(b))
#         self.assertEqual('a', self.read_file(a))
#         self.assertEqual('b', self.read_file(b))
#
#     def test_package_create_script(self):
#         """watcher should build every new script in package"""
#
#
#         # Prepare files:
#         self.create_file('script.py',
#                          'from stado import route\nroute("/a.html", "a")')
#
#         # Assumptions:
#         self.stop_on_create_script('new.py')
#
#         # Action:
#         self.run_command(args='')
#         self.create_file('new.py',
#                          'from stado import route\nroute("/b.html", "b")')
#         self.wait()
#
#         # Tests:
#         a = os.path.join(config.build_dir, 'a.html')
#         b = os.path.join(config.build_dir, 'b.html')
#         self.assertTrue(os.path.exists(a))
#         self.assertTrue(os.path.exists(b))
#         self.assertEqual('a', self.read_file(a))
#         self.assertEqual('b', self.read_file(b))
#
#
#


#
#
# class TestWatch(TestCommand):
#     """Command watch
#
#     Important!
#     This test is done in temporary directory. Use self.temp_path to get path to it.
#     During tests current working directory is self.temp_path. Previous working
#     directory is self.cwd.
#
#     """
#
#     _command = 'watch'
#
#     def setUp(self):
#         TestCommand.setUp(self)
#
#         # For faster checking files changes.
#         self.console.set_interval(0.1)
#         # After first rebuild stop command.
#         self.console.after_rebuild = self.console.stop_waiting
#
#     # Shortcut functions.
#
#     def queue_modify_file(self, *path):
#         """Append " updated" data to given file."""
#
#         def modify(path):
#             with open(path, 'a') as file:
#                 file.write(' updated')
#         self.console.before_waiting = (modify,
#                                        [os.path.join(self.temp_path, *path)])
#
#     def queue_modify_script(self, *path):
#         """Modify python script file."""
#
#         def modify(path):
#             with open(path, 'w') as file:
#                 script = \
#                     (
#                         '\nfrom stado import Site'
#                         '\nsite = Site()'
#                         '\nsite.route("/test.html", "test")'
#                     )
#                 file.write(script)
#         self.console.before_waiting = (modify,
#                                        [os.path.join(self.temp_path, *path)])
#
#     def queue_create_file(self, *path):
#         """Creates new file with "hello world" data."""
#
#         def create(path):
#             with open(path, 'w') as file:
#                 file.write('hello')
#         self.console.before_waiting = (create,
#                                        [os.path.join(self.temp_path, *path)])
#
#     def remove_file(self, *path):
#         """BE CAREFUL! Removes given file."""
#         os.remove(os.path.join(self.temp_path, *path))
#
#     def remove_directory(self, *path):
#         """BE CAREFUL! Removes directory recursively."""
#         p = os.path.join(os.path.join(self.temp_path, *path))
#         shutil.rmtree(p)
#
#     # Module
#
#     def test_return(self):
#         """should return True if watching ended successful"""
#
#         # stado.py watch script_a.py
#         # stado.py watch
#         self.queue_modify_file('a.html')
#         self.assertTrue(self.command('script_a.py'))
#         self.assertTrue(self.command())
#
#         # stado.py watch x
#         self.queue_modify_file(os.path.join('x', 'foo.html'))
#         self.assertTrue(self.command('x'))
#
#     # Modifying source files.
#
#     def test_module_modify_file(self):
#         """watcher should react on file modifying [stado.py watch module.py]"""
#
#         # After executing command, modify ~temp/a.html file.
#         self.queue_modify_file('a.html')
#         # Execute command: stado.py watch script_a.py
#         self.command('script_a.py')
#         self.assertEqual('a updated', self.read_file('output_a', 'a.html'))
#
#     def test_package_modify_file(self):
#         """watcher should react on file modifying [stado.py watch package]"""
#
#         self.queue_modify_file('x', 'foo.html')
#         self.command('x')
#         self.assertEqual('bar updated',
#                          self.read_file('x', config.build_dir, 'foo.html'))
#
#     def test_modify_file(self):
#         """watcher should react on file modifying [stado.py watch]"""
#
#         self.queue_modify_file('a.html')
#         self.command()
#         self.assertEqual('a updated', self.read_file('output_a', 'a.html'))
#
#     # Creating new files.
#
#     def test_module_create_file(self):
#         """watcher should react on file creating [stado.py watch module.py]"""
#
#         self.queue_create_file('new.html')
#         self.command('script_a.py')
#         self.assertEqual('hello', self.read_file('output_a', 'new.html'))
#
#     def test_package_create_file(self):
#         """watcher should react on file creating [stado.py watch package]"""
#
#         self.queue_create_file('x', 'new.html')
#         self.command('x')
#         self.assertEqual('hello',
#                          self.read_file('x', config.build_dir, 'new.html'))
#
#     def test_create_file(self):
#         """watcher should react on file creating [stado.py watch]"""
#
#         self.queue_create_file('new.html')
#         self.command()
#         self.assertEqual('hello', self.read_file('output_a', 'new.html'))
#
#     # Removing files.
#
#     def test_module_remove_file(self):
#         """watcher should react on file removing [stado.py watch module.py]"""
#
#         def remove():
#             """Clears output directory and removes one source file."""
#             self.remove_directory('output_a')
#             self.remove_file('a.html')
#
#         self.console.before_waiting = remove
#         self.command('script_a.py')
#         path = os.path.join(self.temp_path, 'output_a', 'a.html')
#         self.assertFalse(os.path.exists(path))
#
#     def test_package_remove_file(self):
#         """watcher should react on file removing [stado.py watch package]"""
#
#         def remove():
#             """Clears output directory and removes one source file."""
#             self.remove_directory('x', config.build_dir)
#             self.remove_file('x', 'foo.html')
#
#         self.console.before_waiting = remove
#         self.command('x')
#         path = os.path.join(self.temp_path, config.build_dir, 'foo.html')
#         self.assertFalse(os.path.exists(path))
#
#     # Modifying python script file.
#
#     def test_module_modify_script(self):
#         """watcher should re-import modified script [stado.py watch module.py]"""
#
#         self.queue_modify_script('script_a.py')
#         self.command('script_a.py')
#         self.assertEqual('test', self.read_file(config.build_dir, 'test.html'))
#
#     def test_package_modify_script(self):
#         """watcher should re-import modified script [stado.py watch package]"""
#
#         self.queue_modify_script('x', 'script.py')
#         self.command('x')
#         self.assertEqual('test',
#                          self.read_file('x', config.build_dir, 'test.html'))
#
#     def test_modify_script(self):
#         """watcher should re-import modified script [stado.py watch]"""
#
#         self.queue_modify_script('script_a.py')
#         self.command()
#         self.assertEqual('test', self.read_file(config.build_dir, 'test.html'))
#
#     # Adding new python scripts.
#
#     def test_module_create_site(self):
#         """watcher should build every new site instance in module"""
#
#         def modify():
#             with open(os.path.join(self.temp_path, 'script_a.py'), 'w') as file:
#                 script = \
#                     (
#                         '\nfrom stado import Site'
#                         '\na = Site()'
#                         '\na.route("/a.html", "a")'
#                         '\nb = Site()'
#                         '\nb.route("/b.html", "b")'
#                     )
#                 file.write(script)
#
#         self.console.before_waiting = modify
#         self.command('script_a.py')
#         self.assertEqual('a', self.read_file(config.build_dir, 'a.html'))
#         self.assertEqual('b', self.read_file(config.build_dir, 'b.html'))
#
#     def test_package_create_script(self):
#         """watcher should build every new script in package"""
#
#         def modify_script():
#             self.console.after_rebuild = self.console.stop_waiting
#
#             with open(os.path.join(self.temp_path, 'x', 'x.py'), 'w') as file:
#                 script = \
#                     (
#                         '\nfrom stado import Site'
#                         '\na = Site("foo", output="out")'
#                         '\na.route("/a.html", "b")'
#                     )
#                 file.write(script)
#
#         def create_script():
#             with open(os.path.join(self.temp_path, 'x', 'x.py'), 'w') as file:
#                 script = \
#                     (
#                         '\nfrom stado import Site'
#                         '\na = Site("foo", output="out")'
#                         '\na.route("/a.html", "a")'
#                     )
#                 file.write(script)
#
#             self.console.after_rebuild = modify_script
#
#         self.console.before_waiting = create_script
#         self.command('x')
#         self.assertEqual('b', self.read_file('x', 'foo', 'out', 'a.html'))
#
#     # Removing python script.
#
#     def test_package_remove_script(self):
#
#         i = 0
#         def remove():
#             nonlocal i
#             i = len(self.console.commands['watch'].file_monitor.watchers)
#             os.remove(os.path.join(self.temp_path, 'script_b.py'))
#
#         self.console.before_waiting = remove
#         self.command()
#         # self.assertEqual(i - 1, )
#
#     # TODO:
#     # def test_module_remove_site(self):
#     #
#     #     def modify():
#     #         with open(os.path.join(self.temp_path, 'script_a.py'), 'w') as file:
#     #             file.write('pass')
#     #
#     #     self.console.before_waiting = modify
#     #     self.command('script_a.py')
#     #     self.assertEqual('a', self.read_file(config.build_dir, 'a.html'))
#     #     self.assertEqual('b', self.read_file(config.build_dir, 'b.html'))
#
#     # TODO:
#     # def test_package_remove_script(self):
#     #
#     #     def modify():
#     #         os.remove(os.path.join(self.temp_path, 'script_b.py'))
#     #         with open(os.path.join(self.temp_path, 'g.html'), 'w') as file:
#     #             file.write('pass')
#     #
#     #     self.console.before_waiting = modify
#     #     self.command()
#
#     # Multiple rebuilding.
#
#     def test_rebuild(self):
#         """watcher should correctly rebuilds sites multiple times"""
#
#         def second_rebuild():
#             self.console.after_rebuild = self.console.stop_waiting
#             path = os.path.join(self.temp_path, 'z', 'b', 'new.html')
#             with open(path, 'w') as file:
#                 file.write('hello b')
#
#         def rebuild():
#             self.console.after_rebuild = second_rebuild
#             path = os.path.join(self.temp_path, 'z', 'a', 'new.html')
#             with open(path, 'w') as file:
#                 file.write('hello a')
#
#         # After first rebuild trigger another one.
#         self.console.after_rebuild = rebuild
#         self.queue_create_file('z', 'a', 'new.html')
#         self.command('z')
#
#         self.assertEqual('hello a', self.read_file('z', 'a', 'output', 'new.html'))
#         self.assertEqual('hello b', self.read_file('z', 'b', 'output', 'new.html'))
#
#     # TODO: Removing files?
#     # TODO: Adding another site object to already existing script.