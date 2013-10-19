import os
import unittest
from stado import loaders


class TestLoaders(unittest.TestCase):
    """Tests loaders loading."""

    def test_loading(self):
        """Loading should correctly import loader modules."""

        modules = [i.name for i in loaders.load()]

        self.assertIn('html', modules)
        self.assertIn('json', modules)
        self.assertIn('yaml', modules)


    def test_loading_with_select(self):
        """Loading should correctly import only selected loader modules."""

        modules = [i.name for i in loaders.load(['html'])]

        self.assertIn('html', modules)
        self.assertNotIn('json', modules)
        self.assertNotIn('yaml', modules)
