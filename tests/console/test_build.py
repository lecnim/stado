"""Tests command: build"""

import os
from stado import config
from tests.console import TestCommand


class TestBuild(TestCommand):
    """Command build

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    _command = 'build'

    #

    def test_return(self):
        """should return True if building successful"""

        self.assertTrue(self.command('script_a.py'))
        self.assertTrue(self.command('x'))
        self.assertTrue(self.command())

    #

    def test_module_output(self):
        """should correctly build module file [stado.py build module.py]"""

        self.command('script_a.py')
        # ~temp/output_a
        self.assertEqual('a', self.read_file('output_a', 'a.html'))

        # Check output directory content.
        self.assertCountEqual(['a.html'], os.listdir('output_a'))

    def test_package_output(self):
        """should correctly build package directory [stado.py build package]"""

        # ~temp/x

        self.command('x')
        self.assertEqual('bar', self.read_file('x', config.build_dir,
                                               'foo.html'))

        path = os.path.join(self.temp_path, 'x', 'foo', config.build_dir)
        self.assertFalse(os.path.exists(path),
                         msg='Should run scrips only from top directory!')

        # ~temp/y

        self.command('y')
        self.assertEqual('a', self.read_file('y', config.build_dir, 'a.html'))
        self.assertEqual('b', self.read_file('y', config.build_dir, 'b.html'))

    def test_output(self):
        """should correctly build current directory [stado.py build]"""

        self.command()
        self.assertEqual('a', self.read_file('output_a', 'a.html'))
        self.assertEqual('b', self.read_file('output_b', 'b.html'))

        # Check output directory content.
        self.assertCountEqual(['a.html'], os.listdir('output_a'))
        self.assertCountEqual(['b.html'], os.listdir('output_b'))

    #

    def test_relative_path(self):
        """should accepts relative path as an argument"""

        self.command(os.path.join('x', 'foo', 'script.py'))
        self.assertEqual('bar', self.read_file('x', 'foo', config.build_dir,
                                               'foo', 'foo.html'))

    def test_absolute_path(self):
        """should accepts absolute path a an argument"""

        p = os.path.join(self.temp_path, 'x')
        self.command(os.path.join(p, 'script.py'))
        self.assertEqual('bar', self.read_file(p, config.build_dir, 'foo.html'))