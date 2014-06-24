"""Tests command: watch"""

import os
import shutil
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

    def remove_file(self, *path):
        """BE CAREFUL! Removes given file."""
        os.remove(os.path.join(self.temp_path, *path))

    def remove_directory(self, *path):
        """BE CAREFUL! Removes directory recursively."""
        p = os.path.join(os.path.join(self.temp_path, *path))
        shutil.rmtree(p)

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

    # Removing files.

    def test_module_remove_file(self):
        """watcher should react on file removing [stado.py watch module.py]"""

        def remove():
            """Clears output directory and removes one source file."""
            self.remove_directory('output_a')
            self.remove_file('a.html')

        self.console.before_waiting = remove
        self.command('script_a.py')
        path = os.path.join(self.temp_path, 'output_a', 'a.html')
        self.assertFalse(os.path.exists(path))

    def test_package_remove_file(self):
        """watcher should react on file removing [stado.py watch package]"""

        def remove():
            """Clears output directory and removes one source file."""
            self.remove_directory('x', config.build_dir)
            self.remove_file('x', 'foo.html')

        self.console.before_waiting = remove
        self.command('x')
        path = os.path.join(self.temp_path, config.build_dir, 'foo.html')
        self.assertFalse(os.path.exists(path))

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

    # Adding new python scripts.

    def test_module_create_site(self):
        """watcher should build every new site instance in module"""

        def modify():
            with open(os.path.join(self.temp_path, 'script_a.py'), 'w') as file:
                script = \
                    (
                        '\nfrom stado import Site'
                        '\na = Site()'
                        '\na.route("/a.html", "a")'
                        '\nb = Site()'
                        '\nb.route("/b.html", "b")'
                    )
                file.write(script)

        self.console.before_waiting = modify
        self.command('script_a.py')
        self.assertEqual('a', self.read_file(config.build_dir, 'a.html'))
        self.assertEqual('b', self.read_file(config.build_dir, 'b.html'))

    def test_package_create_script(self):
        """watcher should build every new script in package"""

        def modify():
            with open(os.path.join(self.temp_path, 'x', 'x.py'), 'w') as file:
                script = \
                    (
                        '\nfrom stado import Site'
                        '\na = Site("foo", output="out")'
                        '\na.route("/a.html", "a")'
                    )
                file.write(script)

        self.console.before_waiting = modify
        self.command('x')
        self.assertEqual('a', self.read_file('x', 'foo', 'out', 'a.html'))

    # Removing python script.

    # TODO:
    # def test_module_remove_site(self):
    #
    #     def modify():
    #         with open(os.path.join(self.temp_path, 'script_a.py'), 'w') as file:
    #             file.write('pass')
    #
    #     self.console.before_waiting = modify
    #     self.command('script_a.py')
    #     self.assertEqual('a', self.read_file(config.build_dir, 'a.html'))
    #     self.assertEqual('b', self.read_file(config.build_dir, 'b.html'))

    # TODO:
    # def test_package_remove_script(self):
    #
    #     def modify():
    #         os.remove(os.path.join(self.temp_path, 'script_b.py'))
    #         with open(os.path.join(self.temp_path, 'g.html'), 'w') as file:
    #             file.write('pass')
    #
    #     self.console.before_waiting = modify
    #     self.command()

    # Multiple rebuilding.

    def test_rebuild(self):
        """watcher should correctly rebuilds sites multiple times"""

        def second_rebuild():
            self.console.after_rebuild = self.console.stop_waiting
            path = os.path.join(self.temp_path, 'z', 'b', 'new.html')
            with open(path, 'w') as file:
                file.write('hello b')

        def rebuild():
            self.console.after_rebuild = second_rebuild
            path = os.path.join(self.temp_path, 'z', 'a', 'new.html')
            with open(path, 'w') as file:
                file.write('hello a')

        # After first rebuild trigger another one.
        self.console.after_rebuild = rebuild
        self.queue_create_file('z', 'a', 'new.html')
        self.command('z')

        self.assertEqual('hello a', self.read_file('z', 'a', 'output', 'new.html'))
        self.assertEqual('hello b', self.read_file('z', 'b', 'output', 'new.html'))

    # TODO: Removing files?
    # TODO: Adding another site object to already existing script.