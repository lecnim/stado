"""Tests command: build"""

import os
import tempfile
import shutil

from stado import config
from stado.console import Console
from tests.console import TestCommand


class TestBuildModule(TestCommand):

    def test_return(self):
        self.assertTrue(Console().__call__('build script_a.py'))

    def test_output(self):

        Console().__call__('build script_a.py')

        # ~temp/output_a
        p = os.path.join(self.temp_path, 'output_a')
        self.assertTrue(os.path.exists(p))

        with open(os.path.join(p, 'a.html')) as page:
            self.assertEqual('a', page.read())


class TestBuildPackage(TestCommand):

    def test_return(self):
        self.assertTrue(Console().__call__('build y'))

    def test_output(self):

        Console().__call__('build y')

        # ~temp/y/output
        p = os.path.join(self.temp_path, 'y', config.build_dir)
        self.assertTrue(os.path.exists(p))

        with open(os.path.join(p, 'a.html')) as page:
            self.assertEqual('a', page.read())

        with open(os.path.join(p, 'b.html')) as page:
            self.assertEqual('b', page.read())

class TestBuild(TestCommand):

    def test_return(self):
        self.assertTrue(Console().__call__('build'))

        Console().__call__('build')

        # ~temp/output_a
        # ~temp/output_b
        a = os.path.join(self.temp_path, 'output_a')
        b = os.path.join(self.temp_path, 'output_b')
        self.assertTrue(os.path.exists(a))
        self.assertTrue(os.path.exists(b))

        with open(os.path.join(a, 'a.html')) as page:
            self.assertEqual('a', page.read())
        with open(os.path.join(b, 'b.html')) as page:
            self.assertEqual('b', page.read())


# class TestBuildDirectory(TestCommand):
#     """Command build <site>:
#
#     Important!
#     This test is done in temporary directory. Use self.temp_path to get path to it.
#     During tests current working directory is self.temp_path. Previous working
#     directory is self.cwd.
#
#     """
#
#     def test_returned_value(self):
#         """should return True if building successful."""
#
#         self.assertTrue(Console().__call__('build a'))
#
#
#     def test_build_directory(self):
#         """should create output directory in site directory."""
#
#         Console().__call__('build a')
#
#         # temp/a/_build
#         build_directory = os.path.join(self.temp_path, 'a', config.build_dir)
#         self.assertTrue(os.path.exists(build_directory))
#
#
#     def test_page(self):
#         """should correctly build page from site content."""
#
#         Console().__call__('build a')
#
#         # temp/a/_build
#         build_directory = os.path.join(self.temp_path, 'a', config.build_dir)
#
#         self.assertListEqual(['a.html'], os.listdir(build_directory))
#         with open(os.path.join(build_directory, 'a.html')) as page:
#             self.assertEqual('hello world', page.read())
#
#
#     def test_skip_python_script(self):
#         """should skip python files."""
#
#         Console().__call__('build a')
#
#         # temp/a/_build/site.py
#         site_py = os.path.join(self.temp_path, 'a', config.build_dir, 'site.py')
#
#         self.assertFalse(os.path.exists(site_py))
#
#
#     def test_output_option(self):
#         """--output: should build site in custom output directory."""
#
#         output_path = tempfile.mkdtemp()
#         Console().__call__('build a --output ' + output_path)
#
#         self.assertListEqual(['a.html'], os.listdir(output_path))
#
#         # Should build site in output directory.
#         path = os.path.join(self.temp_path, 'a')
#         self.assertNotIn(config.build_dir, os.listdir(path))
#
#         shutil.rmtree(output_path)
#
#
#
# class TestBuildWithoutArguments(TestCommand):
#     """Command build:
#
#     Important!
#     This test is done in temporary directory. Use self.temp_path to get path to it.
#     During tests current working directory is self.temp_path. Previous working
#     directory is self.cwd.
#
#     """
#
#     def test_returned_value(self):
#         """should return True if building each site in group => successful."""
#
#         self.assertTrue(Console().__call__('build'))
#
#
#     def test_build_directory(self):
#         """should create output directory in each site directory."""
#
#         Console().__call__('build')
#
#         a = os.path.join(self.temp_path, 'a', config.build_dir)
#         b = os.path.join(self.temp_path, 'b', config.build_dir)
#
#         self.assertTrue(os.path.exists(a))
#         self.assertTrue(os.path.exists(b))
#
#
#     def test_page(self):
#         """should correctly build pages in each site content."""
#
#         Console().__call__('build')
#
#         a = os.path.join(self.temp_path, 'a', config.build_dir, 'a.html')
#         b = os.path.join(self.temp_path, 'b', config.build_dir, 'b.html')
#
#         self.assertTrue(os.path.exists(a))
#         self.assertTrue(os.path.exists(b))
#
#         with open(a) as page:
#             self.assertEqual('hello world', page.read())
#         with open(b) as page:
#             self.assertEqual('hello world', page.read())
#
#
#     def test_skip_python_script(self):
#         """should skip python files."""
#
#         Console().__call__('build')
#
#         a = os.path.join(self.temp_path, 'a', config.build_dir, 'site.py')
#         b = os.path.join(self.temp_path, 'b', config.build_dir, 'site.py')
#
#         self.assertFalse(os.path.exists(a))
#         self.assertFalse(os.path.exists(b))
#
#
#     def test_output_option(self):
#         """--output: should build each site in custom output directory."""
#
#         output_path = tempfile.mkdtemp()
#         Console().__call__('build --output ' + output_path)
#
#         self.assertCountEqual(['a', 'b'], os.listdir(output_path))
