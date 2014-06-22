"""Tests command: watch"""

import os
from stado import config
from tests.console import TestCommand


class TestWatch(TestCommand):
    """Command watch

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    _command = 'watch'

    def setUp(self):
        TestCommand.setUp(self)

        # For faster checking files changes.
        self.console.set_interval(0.1)
        # After first rebuild stop command.
        self.console.after_rebuild = self.console.stop_waiting

    # Shortcut functions.

    def queue_modify_file(self, *path):
        """Append " updated" data to given file."""

        def modify(path):
            with open(path, 'a') as file:
                file.write(' updated')
        self.console.before_waiting = (modify,
                                       [os.path.join(self.temp_path, *path)])

    def queue_modify_script(self, *path):
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
        self.console.before_waiting = (modify,
                                       [os.path.join(self.temp_path, *path)])

    def queue_create_file(self, *path):
        """Creates new file with "hello world" data."""

        def create(path):
            with open(path, 'w') as file:
                file.write('hello')
        self.console.before_waiting = (create,
                                       [os.path.join(self.temp_path, *path)])

    # Module

    def test_return(self):
        """should return True if watching ended successful"""

        # stado.py watch script_a.py
        # stado.py watch
        self.queue_modify_file('a.html')
        self.assertTrue(self.command('script_a.py'))
        self.assertTrue(self.command())

        # stado.py watch x
        self.queue_modify_file(os.path.join('x', 'foo.html'))
        self.assertTrue(self.command('x'))

    # Modifying source files.

    def test_module_modify_file(self):
        """watcher should react on file modifying [stado.py watch module.py]"""

        # After executing command, modify ~temp/a.html file.
        self.queue_modify_file('a.html')
        # Execute command: stado.py watch script_a.py
        self.command('script_a.py')
        self.assertEqual('a updated', self.read_file('output_a', 'a.html'))

    def test_package_modify_file(self):
        """watcher should react on file modifying [stado.py watch package]"""

        self.queue_modify_file('x', 'foo.html')
        self.command('x')
        self.assertEqual('bar updated',
                         self.read_file('x', config.build_dir, 'foo.html'))

    def test_modify_file(self):
        """watcher should react on file modifying [stado.py watch]"""

        self.queue_modify_file('a.html')
        self.command()
        self.assertEqual('a updated', self.read_file('output_a', 'a.html'))

    # Creating new files.

    def test_module_create_file(self):
        """watcher should react on file creating [stado.py watch module.py]"""

        self.queue_create_file('new.html')
        self.command('script_a.py')
        self.assertEqual('hello', self.read_file('output_a', 'new.html'))

    def test_package_create_file(self):
        """watcher should react on file creating [stado.py watch package]"""

        self.queue_create_file('x', 'new.html')
        self.command('x')
        self.assertEqual('hello',
                         self.read_file('x', config.build_dir, 'new.html'))

    def test_create_file(self):
        """watcher should react on file creating [stado.py watch]"""

        self.queue_create_file('new.html')
        self.command()
        self.assertEqual('hello', self.read_file('output_a', 'new.html'))

    # Modifying python script file.

    def test_module_modify_script(self):
        """watcher should re-import modified script [stado.py watch module.py]"""

        self.queue_modify_script('script_a.py')
        self.command('script_a.py')
        self.assertEqual('test', self.read_file(config.build_dir, 'test.html'))

    def test_package_modify_script(self):
        """watcher should re-import modified script [stado.py watch package]"""

        self.queue_modify_script('x', 'script.py')
        self.command('x')
        self.assertEqual('test',
                         self.read_file('x', config.build_dir, 'test.html'))

    def test_modify_script(self):
        """watcher should re-import modified script [stado.py watch]"""

        self.queue_modify_script('script_a.py')
        self.command()
        self.assertEqual('test', self.read_file(config.build_dir, 'test.html'))

    # Multiple rebuilding.

    def test_module_rebuild(self):
        """watcher should correctly rebuilds sites multiple times"""

        def function():
            """Creates new file 'x.html'"""
            self.console.after_rebuild = self.console.stop_waiting
            with open(os.path.join(self.temp_path, 'x.html'), 'w') as file:
                file.write('hello')

        # After first rebuild trigger another one.
        self.console.after_rebuild = function
        self.queue_create_file('new.html')
        self.command('script_a.py')

        self.assertEqual('hello', self.read_file('output_a', 'new.html'))
        self.assertEqual('hello', self.read_file('output_a', 'x.html'))


    # TODO: Removing files?
    # TODO: Adding another site object to already existing script.
