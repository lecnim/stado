import unittest
import shutil
import tempfile
import os
import inspect

from stado.console import Console


class TestExample(unittest.TestCase):

    @property
    def path(self):
        return os.path.dirname(inspect.getfile(self.__class__))

    @property
    def output(self):
        return os.path.join(self.path, 'output')

    def setUp(self):
        self.cwd = os.getcwd()



        os.chdir(self.path)

        self.temp_path = tempfile.mkdtemp()

        self.console = Console()
        self.console('build data --output ' + self.temp_path)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.temp_path)

    # Comparing outputs.

    def compare_outputs(self, path=''):
        """Checks if files in test/output directory are same as generated in
        site output. Argument path is patch relative to output directory."""

        output = os.path.join(self.output, path)

        for i in os.listdir(output):
            output_path = os.path.join(output, i)
            if os.path.isfile(output_path):

                test_path = os.path.join(self.temp_path, path, i)

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
        test_files = self.get_files(self.temp_path)
        self.assertCountEqual(output_files, test_files)

    def get_files(self, path):
        """Returns all files path tree."""

        paths = []
        for i in os.walk(path):
            for file in i[2]:
                paths.append(os.path.join(os.path.relpath(i[0], path), file))
        return paths
