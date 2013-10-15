import unittest

from stado import loaders
from stado.loaders import html, json, yaml

class TestLoaders(unittest.TestCase):

    def test_loading(self):
        """Loading should correctly import loader modules."""

        returned = loaders.load()
        self.assertIsInstance(returned, tuple)

        enabled = returned[0]
        self.assertIsInstance(enabled, list)
        self.assertIn(html, enabled)
        self.assertIn(json, enabled)
        self.assertIn(yaml, enabled)


    def test_loading_with_select(self):
        """Loading should correctly import only selected loader modules."""

        enabled, disabled = loaders.load(['html'])

        self.assertIn(html, enabled)
        self.assertNotIn(json, disabled)
        self.assertNotIn(yaml, disabled)
