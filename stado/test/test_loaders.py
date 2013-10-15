import unittest
from stado import loaders

class TestLoaders(unittest.TestCase):
    """Tests loaders loading."""

    def test_loading(self):
        """Loading should correctly import loader modules."""

        modules = [i.__name__ for i in loaders.load()]

        self.assertIn('html', modules)
        self.assertIn('json_pages', modules)
        self.assertIn('yaml_pages', modules)


    def test_loading_with_select(self):
        """Loading should correctly import only selected loader modules."""

        modules = [i.__name__ for i in loaders.load(['html'])]

        self.assertIn('html', modules)
        self.assertNotIn('json', modules)
        self.assertNotIn('yaml', modules)
