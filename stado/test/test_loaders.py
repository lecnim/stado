import unittest

from stado import loaders
from stado.loaders import html, json, yaml

class TestLoaders(unittest.TestCase):

    def test_importing(self):
        """Importing should correctly import parser modules."""

        returned = loaders.load()
        self.assertIsInstance(returned, tuple)

        enabled = returned[0]
        self.assertIsInstance(enabled, list)
        self.assertIn(html, enabled)
        self.assertIn(json, enabled)
        self.assertIn(yaml, enabled)