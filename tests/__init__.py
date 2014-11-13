import unittest
import urllib
import tempfile
import shutil
import os
import inspect
import time

from stado import config
from stado.libs import yaml

class BaseTest(unittest.TestCase):



    def setUp(self):

        # Path pointing to current working directory.
        self.cwd = os.getcwd()
        # Path to commands test directory.
        self.path = os.path.dirname(__file__)
        # Path to temporary directory with sites.
        self.temp_path = tempfile.mkdtemp()
        # Set current working directory to temporary directory with sites.
        os.chdir(self.temp_path)

    def tearDown(self):
        # Go to previous working directory and clear files.
        os.chdir(self.cwd)
        shutil.rmtree(self.temp_path)


    #
    # File system shortcuts.
    #

    def wait_until_file_equal(self, path, data):

        path = path.format(output=config.build_dir)

        def read_file():

            while not os.path.exists(path):
                time.sleep(0.25)

            with open(path, 'r') as file:
                return file.read()


        while read_file() != data:
            time.sleep(0.25)


    def prepare_files(self, x):

        for path, data in yaml.load(x).items():
            self.new_file(path, data)


    def read_url(self, url, host, port):
        url = 'http://{}:{}/{}'.format(host, port, url)
        return urllib.request.urlopen(url).read().decode('UTF-8')

    def read_file(self, path):
        """Returns data from given path. Use '/' as a path separator,
        path must be relative to current temp path."""

        if os.path.isabs(path):
            raise ValueError('path must be relative!')

        fp = os.path.join(self.temp_path, *path.split('/'))
        self.assertTrue(os.path.exists(fp),
                        msg='path not found: ' + fp)
        with open(fp) as file:
            return file.read()

    def create_file(self, *args, **kwargs):
        self.new_file(*args, **kwargs)

    def new_file(self, path, data='hello world'):
        """Creates a new file with a data. Use '/' as a path separator,
        path must be relative to temp."""

        if os.path.isabs(path):
            raise ValueError('path must be relative!')

        path = os.path.join(self.temp_path, *path.split('/'))
        dir_path = os.path.dirname(path)

        # Create missing dirs.
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(path, 'w') as file:
            data = data.format(output=config.build_dir)
            file.write(data)

    def create_dir(self, path):
        """Creates a new directory. Use '/' as a path separator,
        path must be relative to temp."""

        if os.path.isabs(path):
            raise ValueError('path must be relative!')

        path = os.path.join(self.temp_path, *path.split('/'))
        os.makedirs(path)

    def modify_file(self, path, data='UPDATE'):
        """Modifies a file data. Use '/' as a path separator,
        path must be relative to temp."""

        if os.path.isabs(path):
            raise ValueError('path must be relative!')

        with open(os.path.join(self.temp_path, *path.split('/')), 'w') as file:
            file.write(data)

    def remove_file(self, path):
        """BE CAREFUL! Removes given file. Use '/' as a path separator,
        path must be relative to temp."""

        if os.path.isabs(path):
            raise ValueError('path must be relative!')
        os.remove(os.path.join(self.temp_path, *path.split('/')))

    def remove_dir(self, path):
        """BE CAREFUL! Removes directory recursively. Use '/' as a path
        separator, path must be relative to temp."""

        if os.path.isabs(path):
            raise ValueError('path must be relative!')

        path = path.format(output=config.build_dir)
        p = os.path.join(self.temp_path, *path.split('/'))
        shutil.rmtree(p)



    # Shortcuts

    def _clear_path(self, path):
        # TODO: !! work in progress
        if os.path.isabs(path):
            mount, path = os.path.splitdrive(path)

        p = path.split('/')
        p = os.path.join(*p)

    def count_files(self, path, amount):
        self.assertCountFiles(path, amount)
    def same_files(self, a, b):
        self.assertSameFiles(a, b)
    def file_equal(self, path, expected):
        self.assertFileEqual(path, expected)
    def eq(self, excepted, actual):
        self.assertEqual(excepted, actual)
    def true(self, a):
        self.assertTrue(a)
    def false(self, a):
        self.assertFalse(a)
    # def raises(self,):


    # def url_equal(self, url, host, port, expected):
    #
    #     data = self.read_url(url, host, port)
    #
    #     if expected != data:
    #         raise AssertionError('Url data is different:\n'
    #                              'url: {}\n'
    #                              'host: {}\n'
    #                              'port: {}\n'
    #                              'actual: {}\n'
    #                              'expected: {}'.format(url, host, port,
    #                                                    data, expected))


    def url_equal(self, url, expected):

        url = url.format(host=config.host, port=config.port)
        data = urllib.request.urlopen(url).read().decode('UTF-8')

        if expected != data:
            raise AssertionError('Url data is different:\n'
                                 'url: {}\n'
                                 'actual: {}\n'
                                 'expected: {}'.format(url, data, expected))


    def assertCountFiles(self, path, amount):



        path = path.format(output=config.build_dir)

        actual = len(os.listdir(path))
        if actual != amount:
            raise AssertionError('Files amount in directory not match:\n'
                                 'path: {}\n'
                                 'actual: {}\n'
                                 'expected: {}'.format(path, actual, amount))

    def assertSameFiles(self, a, b):

        a = a.format(output=config.build_dir)
        b = b.format(output=config.build_dir)

        try:
            with open(a) as file:
                a = file.read()
            with open(b) as file:
                b = file.read()
        except (IOError, OSError) as e:
            raise AssertionError(str(e))

        if a != b:
            raise AssertionError('Files are not the same:\n'
                                 '{}\n'
                                 '{}'.format(a, b))

    def assertFileEqual(self, path, expected):

        path = path.format(output=config.build_dir)

        try:
            with open(path) as file:
                actual = file.read()
        except (IOError, OSError) as e:
            raise AssertionError(str(e))

        if actual != expected:
            raise AssertionError('File data is different:\n'
                                 'path: {}\n'
                                 'actual: {}\n'
                                 'expected: {}'.format(path, actual, expected))


# class TestStado(unittest.TestCase):
#
#     """Base Stado test case."""
#
#
#     def setUp(self):
#
#         # Path pointing to current working directory.
#         self.cwd = os.getcwd()
#         # Path to commands test directory.
#         self.path = os.path.dirname(__file__)
#         # Path to temporary directory with sites.
#         self.temp_path = tempfile.mkdtemp()
#         # Set current working directory to temporary directory with sites.
#         os.chdir(self.temp_path)
#
#     def tearDown(self):
#         # Go to previous working directory and clear files.
#         os.chdir(self.cwd)
#         shutil.rmtree(self.temp_path)
#
#     #
#     # Shortcuts
#     #
#
#     def read_url(self, url, host, port):
#         url = 'http://{}:{}/{}'.format(host, port, url)
#         return urllib.request.urlopen(url).read().decode('UTF-8')
#
#     def read_file(self, path):
#         """Returns data from given path. Use '/' as a path separator,
#         path must be relative to current temp path."""
#
#         if os.path.isabs(path):
#             raise ValueError('path must be relative!')
#
#         fp = os.path.join(self.temp_path, *path.split('/'))
#         self.assertTrue(os.path.exists(fp),
#                         msg='path not found: ' + fp)
#         with open(fp) as file:
#             return file.read()
#
#     def create_file(self, path, data='hello world'):
#         """Creates a new file with a data. Use '/' as a path separator,
#         path must be relative to temp."""
#
#         if os.path.isabs(path):
#             raise ValueError('path must be relative!')
#
#         path = os.path.join(self.temp_path, *path.split('/'))
#         dir_path = os.path.dirname(path)
#
#         # Create missing dirs.
#         if not os.path.exists(dir_path):
#             os.makedirs(dir_path)
#
#         with open(path, 'w') as file:
#             file.write(data)
#
#     def create_dir(self, path):
#         """Creates a new directory. Use '/' as a path separator,
#         path must be relative to temp."""
#
#         if os.path.isabs(path):
#             raise ValueError('path must be relative!')
#
#         path = os.path.join(self.temp_path, *path.split('/'))
#         os.makedirs(path)
#
#     def modify_file(self, path, data='UPDATE'):
#         """Modifies a file data. Use '/' as a path separator,
#         path must be relative to temp."""
#
#         if os.path.isabs(path):
#             raise ValueError('path must be relative!')
#
#         with open(os.path.join(self.temp_path, *path.split('/')), 'w') as file:
#             file.write(data)
#
#     def remove_file(self, path):
#         """BE CAREFUL! Removes given file. Use '/' as a path separator,
#         path must be relative to temp."""
#
#         if os.path.isabs(path):
#             raise ValueError('path must be relative!')
#         os.remove(os.path.join(self.temp_path, *path.split('/')))
#
#     def remove_dir(self, path):
#         """BE CAREFUL! Removes directory recursively. Use '/' as a path
#         separator, path must be relative to temp."""
#
#         if os.path.isabs(path):
#             raise ValueError('path must be relative!')
#         p = os.path.join(self.temp_path, *path.split('/'))
#         shutil.rmtree(p)


class TestTemporaryDirectory(unittest.TestCase):

    def setUp(self):
        self.temp_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_path)



class TestInCurrentDirectory(unittest.TestCase):

    @property
    def path(self):
        return os.path.dirname(inspect.getfile(self.__class__))

    def setUp(self):
        self.cwd = os.getcwd()
        os.chdir(self.path)

    def tearDown(self):
        os.chdir(self.cwd)
