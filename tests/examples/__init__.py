import unittest
import shutil
import tempfile
import os
import inspect

from stado.console import Console
from stado import config
from stado.utils import copytree


class TestExample(unittest.TestCase):
    """Base class for example tests."""

    @property
    def path(self):
        """Path to current example test directory, for example: ~/jsonfruits"""
        return os.path.dirname(inspect.getfile(self.__class__))

    @property
    def output(self):
        """Path to current example test output directory,
        for example: ~/jsonfruits/output"""
        return os.path.join(self.path, 'output')

    def setUp(self):

        self.cwd = os.getcwd()

        # Copy example test 'data' directory content to temporary directory.
        # Change current working directory to temporary directory.
        self.temp_path = tempfile.mkdtemp()
        copytree(os.path.join(self.path, 'data'), self.temp_path)
        os.chdir(self.temp_path)

        # Console will run every python script in temporary directory.
        self.console = Console()
        self.console('build')

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.temp_path)

    # Comparing outputs.

    def compare_outputs(self, path=''):
        """Checks if files in test/output directory are same as generated in
        site output. Argument path is patch relative to output directory."""

        # This path will be compared.
        output = os.path.join(self.output, path)

        for i in os.listdir(output):
            output_path = os.path.join(output, i)
            if os.path.isfile(output_path):
                test_path = os.path.join(self.temp_path, config.build_dir,
                                         path, i)
                # Check if file was created.
                self.assertTrue(os.path.exists(test_path))

                # Compare file sources.
                with open(test_path) as page:
                    with open(output_path) as ok:
                        self.assertEqual(page.read(), ok.read())

            # Check files in next directory.
            else:
                self.compare_outputs(os.path.join(path, i))

        # Compares directory tree.
        output_files = self.get_files(self.output)
        test_files = self.get_files(os.path.join(self.temp_path, config.build_dir))
        self.assertCountEqual(output_files, test_files)

    def get_files(self, path):
        """Returns all files path tree."""

        paths = []
        for i in os.walk(path):
            for file in i[2]:
                paths.append(os.path.join(os.path.relpath(i[0], path), file))
        return paths