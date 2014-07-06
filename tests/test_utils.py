import unittest
from os import path
from stado import utils


class TestUtils(unittest.TestCase):
    """
    A utils module
    """
    def test_is_subpath(self):
        """is_subpath()"""

        self.assertTrue(utils.is_subpath('/foo/bar', '/foo'))
        self.assertTrue(utils.is_subpath('foo/bar', 'foo'))
        self.assertTrue(utils.is_subpath('/foo', '/foo'))
        self.assertTrue(utils.is_subpath('/foo/', '/foo'))
        self.assertTrue(utils.is_subpath('/foo', '/foo/'))
        self.assertTrue(utils.is_subpath('/foo/', '/foo/'))

        self.assertFalse(utils.is_subpath('bar', 'foo/bar'))
        self.assertFalse(utils.is_subpath('/foo', 'foo'))


class TestRelativePath(unittest.TestCase):
    """
    A utils.relative_path() function
    """

    def test(self):
        """should correctly convert paths to elegant relative form"""

        self.assertEqual('a', utils.relative_path('a/'))
        self.assertEqual(path.join('a', 'b'), utils.relative_path('a\\b'))
        self.assertEqual(path.join('a', 'b'), utils.relative_path('a//b'))

    def test_error(self):
        """should raise error if path is absolute"""

        self.assertRaises(ValueError, utils.relative_path, '/a')