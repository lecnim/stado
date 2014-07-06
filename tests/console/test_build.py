"""Tests command: build"""

import os

from stado import config
from tests.console import TestCommandNew
from stado.console import Console
from stado.console.errors import CommandError
from stado.console.cmds.build import Build
import stado


class TestBuild(TestCommandNew):
    """Command build

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to
    it. During tests current working directory is self.temp_path. Previous
    working directory is self.cwd.

    """

    command_class = Build

    #
    # Unit tests
    #

    def test_build_script(self):

        cwd = os.getcwd()

        # Passing directory instead of file.

        self.create_file('dir/x.file')
        self.assertRaises(ValueError, self.command._run_module, 'dir')
        # Clear default site after error.
        self.assertIsNone(stado.site)
        self.assertEqual(cwd, os.getcwd())

        # Path not found.

        self.assertRaises(CommandError, self.command._run_module, 'not.found')
        self.assertIsNone(stado.site)
        self.assertEqual(cwd, os.getcwd())

        # Exception in running module.

        self.create_file('script.py', 'raise ValueError("test")')
        self.assertRaises(ValueError, self.command._run_module, 'script.py')
        self.assertIsNone(stado.site)
        self.assertEqual(cwd, os.getcwd())

    #

    def test_run_return(self):
        """should return True if building successful"""

        self.create_file('script.py', 'from stado import route\n'
                                      'route("/a.html", "a")')
        self.create_file('x/script.py', 'from stado import route\n'
                                        'route("/a.html", "a")')

        self.assertTrue(self.command.run('script.py'))
        self.assertTrue(self.command.run())
        self.assertTrue(self.command.run('x'))

    def test_output(self):
        """should correctly build files in output"""

        # $ stado.py build module.py

        self.create_file('script.py', 'from stado import route\n'
                                      'route("/a.html", "a")')
        self.command.run('script.py')

        self.assertEqual('a', self.read_file(config.build_dir + '/a.html'))
        self.assertCountEqual(['a.html'], os.listdir(config.build_dir))

        # $ stado.py build

        self.create_file('script_b.py',
                         'from stado import Site\n'
                         'Site(output="output_b").route("/b.html", "b")')
        self.command.run()

        self.assertEqual('a', self.read_file(config.build_dir + '/a.html'))
        self.assertEqual('b', self.read_file('output_b/b.html'))
        self.assertCountEqual(['a.html'], os.listdir(config.build_dir))
        self.assertCountEqual(['b.html'], os.listdir('output_b'))

        # $ stado.py build package

        self.create_file('x/script.py', 'from stado import route\n'
                                        'route("/foo.html", "bar")')
        self.create_file('x/foo/script.py', 'from stado import route\n'
                                            'route("/foo.html", "bar")')
        self.command.run('x')

        self.assertEqual('bar',
                         self.read_file('x/' + config.build_dir + '/foo.html'))

        path = os.path.join(self.temp_path, 'x', 'foo', config.build_dir)
        self.assertFalse(os.path.exists(path),
                         msg='Should run scrips only from top directory!')

    def test_relative_path(self):
        """should accept relative path as an argument"""

        self.create_file('x/foo/script.py', 'from stado import route\n'
                                            'route("/foo.html", "bar")')
        self.command.run(os.path.join('x', 'foo', 'script.py'))
        self.assertEqual('bar',
                         self.read_file('x/foo/' + config.build_dir
                                        + '/foo.html'))

    def test_absolute_path(self):
        """should accept absolute path a an argument"""

        self.create_file('x/foo/script.py', 'from stado import route\n'
                                            'route("/foo.html", "bar")')
        p = os.path.join(self.temp_path, 'x', 'foo')
        self.command.run(os.path.join(p, 'script.py'))
        self.assertEqual('bar', self.read_file('x/foo/' + config.build_dir
                                               + '/foo.html'))

    def test_not_found(self):
        """should raise command error if script is not found"""

        self.assertRaises(CommandError, self.command.run, 'not.found')

    #
    # Console.
    #

    def test_console(self):
        """should work with console"""

        # Prepare files.
        self.create_file('script.py',
                         'from stado import route\nroute("/a.html", "a")')

        console = Console()
        console(self.command_class.name)

        self.assertEqual('a', self.read_file(config.build_dir + '/a.html'))

        # Path not found.

        self.assertFalse(console(self.command_class.name + ' not/found'))