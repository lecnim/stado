"""Tests command: watch"""

import os
import tempfile

from stado import config
from stado.console import Console
from tests.console import TestCommand



# # Helpers.
#
# def modify_file(path):
#     """Append ' updated' data to given file."""
#     with open(path, 'a') as file:
#         file.write(' updated')
#
# def create_file(path):
#     """Creates new file with 'hello world' data."""
#     with open(path, 'w') as file:
#        file.write('hello world')
#
# def modify_script(path):
#     """Changes python script."""
#     with open(path, 'w') as file:
#         script = \
#             (
#                 '\nfrom stado import Site'
#                 '\nsite = Site()'
#                 '\npage = site.load("a.html")'
#                 '\npage.source = "updated"'
#                 '\nsite.build(page)'
#             )
#         file.write(script)


class TestWatch(TestCommand):

    _command = 'watch'

    def setUp(self):
        TestCommand.setUp(self)

        self.console = Console()
        # For faster checking files changes.
        self.console.set_interval(0.1)
        # After first rebuild stop command.
        self.console.after_rebuild = self.console.stop_waiting

    # Shortcut functions.

    def modify_file(self, *path):
        """Append " updated" data to given file."""

        def modify(path):
            with open(path, 'a') as file:
                file.write(' updated')
        self.console.before_waiting = (modify, [os.path.join(self.temp_path,
                                                             *path)])

    def modify_script(self, *path):
        """Modify python script file."""

        def modify(path):
            with open(path, 'w') as file:
                script = \
                    (
                        '\nfrom stado import Site'
                        '\nsite = Site()'
                        '\nsite.route("/test.html", "test")'
                    )
                file.write(script)
        self.console.before_waiting = (modify, [os.path.join(self.temp_path,
                                                             *path)])

    def create_file(self, *path):
        """Creates new file with "hello world" data."""

        def create(path):
            with open(path, 'w') as file:
                file.write('hello')

        self.console.before_waiting = (create, [os.path.join(self.temp_path,
                                                             *path)])

    def command(self, arguments=''):
        """Execute console command with given arguments string."""
        return self.console(self._command + ' ' + arguments)

    def read_file(self, *path):
        """Returns data from given path, relative to current temp path."""
        with open(os.path.join(self.temp_path, *path)) as file:
            return file.read()

    # Module

    def test_return(self):
        """should return True if watching ended successful"""

        # stado.py watch script_a.py
        # stado.py watch
        self.modify_file('a.html')
        self.assertTrue(self.command('script_a.py'))
        self.assertTrue(self.command())

        # stado.py watch x
        self.modify_file(os.path.join('x', 'foo.html'))
        self.assertTrue(self.command('x'))

    # Modifying source files.

    def test_module_modify_file(self):
        """watcher should react on file modifying [stado.py watch module.py]"""

        # After executing command, modify ~temp/a.html file.
        self.modify_file('a.html')
        # Execute command: stado.py watch script_a.py
        self.command('script_a.py')
        self.assertEqual('a updated', self.read_file('output_a', 'a.html'))

    def test_package_modify_file(self):
        """watcher should react on file modifying [stado.py watch package]"""

        self.modify_file('x', 'foo.html')
        self.command('x')
        self.assertEqual('bar updated',
                         self.read_file('x', config.build_dir, 'foo.html'))

    def test_modify_file(self):
        """watcher should react on file modifying [stado.py watch]"""

        self.modify_file('a.html')
        self.command()
        self.assertEqual('a updated', self.read_file('output_a', 'a.html'))

    # Creating new files.

    def test_module_create_file(self):
        """watcher should react on file creating [stado.py watch module.py]"""

        self.create_file('new.html')
        self.command('script_a.py')
        self.assertEqual('hello', self.read_file('output_a', 'new.html'))

    def test_package_create_file(self):
        """watcher should react on file creating [stado.py watch package]"""

        self.create_file('x', 'new.html')
        self.command('x')
        self.assertEqual('hello',
                         self.read_file('x', config.build_dir, 'new.html'))

    def test_create_file(self):
        """watcher should react on file creating [stado.py watch]"""

        self.create_file('new.html')
        self.command()
        self.assertEqual('hello', self.read_file('output_a', 'new.html'))

    # Modifying python script file.

    def test_module_modify_script(self):
        """watcher should re-import modified script [stado.py watch module.py]"""

        self.modify_script('script_a.py')
        self.command('script_a.py')
        self.assertEqual('test', self.read_file(config.build_dir, 'test.html'))

    def test_package_modify_script(self):
        """watcher should re-import modified script [stado.py watch package]"""

        self.modify_script('x', 'script.py')
        self.command('x')
        self.assertEqual('test',
                         self.read_file('x', config.build_dir, 'test.html'))

    def test_modify_script(self):
        """watcher should re-import modified script [stado.py watch]"""

        self.modify_script('script_a.py')
        self.command()
        self.assertEqual('test', self.read_file(config.build_dir, 'test.html'))

    # TODO: Removing files?
    # TODO: Adding another site object to already exsting script.

    #
    #
    # def test_create_file(self):
    #     """watcher should react on file creating."""
    #
    #     self.shell.before_waiting = (create_file,
    #                                  [os.path.join(self.temp_path, 'new.html')])
    #     self.shell(self.command + ' script_a.py')
    #
    #     path = os.path.join(self.temp_path, 'output_a', 'new.html')
    #     with open(path) as file:
    #         self.assertEqual('hello world', file.read())


    # def test_modify_script(self):
    #     """watcher should correctly re-import site.py"""
    #
    #     self.shell.before_waiting = (modify_script,
    #                                  [os.path.join(self.temp_path, 'script_a.py')])
    #     self.shell(self.command + ' script_a.py')
    #
    #     path = os.path.join(self.temp_path, config.build_dir, 'a.html')
    #     with open(path) as file:
    #         self.assertEqual('updated', file.read())




    # def test_output_option(self):
    #     """--output: watcher should use custom output directory."""
    #
    #     output_path = tempfile.mkdtemp()
    #
    #     self.shell.before_waiting = (modify_file,
    #                                  [os.path.join(self.temp_path, 'a', 'a.html')])
    #     self.shell(self.command + ' a --output ' + output_path)
    #
    #     path = os.path.join(output_path, 'a.html')
    #     with open(path) as file:
    #         self.assertEqual('hello world updated', file.read())








# class TestWatch(TestCommand):
#     """Command watch group:
#
#     Important!
#     This test is done in temporary directory. Use self.temp_path to get path to it.
#     During tests current working directory is self.temp_path. Previous working
#     directory is self.cwd.
#
#     """
#
#     def setUp(self):
#         TestCommand.setUp(self)
#
#         self.shell = Console()
#         # For faster checking files changes.
#         self.shell.set_interval(0.1)
#         # After first rebuild stop command.
#         self.shell.after_rebuild = self.shell.stop_waiting
#
#
#     def test_return_true(self):
#         """should return True if watching ended successful."""
#
#         self.shell.before_waiting = (modify_file,
#                                      [os.path.join(self.temp_path, 'a', 'a.html')])
#         self.assertTrue(self.shell('watch'))
#
#
#
#
#     def test_modify_site(self):
#         """watcher should rebuild only modified site."""
#
#         self.shell.before_waiting = (modify_file,
#                                      [os.path.join(self.temp_path, 'a', 'a.html')])
#         self.shell('watch')
#
#         path = os.path.join(self.temp_path, 'a', config.build_dir, 'a.html')
#         with open(path) as file:
#             self.assertEqual('hello world updated', file.read())
#
#         # Should not rebuild not modified sites.
#         path = os.path.join(self.temp_path, 'b', config.build_dir)
#         self.assertFalse(os.path.exists(path))


    # def test_output_option(self):
    #     """--output: watcher should use custom output directory."""
    #
    #     output_path = tempfile.mkdtemp()
    #
    #     self.shell.before_waiting = (modify_file,
    #                                  [os.path.join(self.temp_path, 'a', 'a.html')])
    #     self.shell('watch --output ' + output_path)
    #
    #     path = os.path.join(output_path, 'a', 'a.html')
    #     with open(path) as file:
    #         self.assertEqual('hello world updated', file.read())
    #
    #     # Should not rebuild not modified sites.
    #     path = os.path.join(output_path, 'b')
    #     self.assertFalse(os.path.exists(path))
