import unittest
from os import path
from stado import utils

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