import unittest

from stado import parsers
from stado.parsers import html, json, yaml

class TestParsers(unittest.TestCase):

    def test_importing(self):
        """Importing should correctly import parser modules."""

        returned = parsers.import_parsers()
        self.assertIsInstance(returned, tuple)

        enabled = returned[0]
        self.assertIsInstance(enabled, list)
        self.assertIn(html, enabled)
        self.assertIn(json, enabled)
        self.assertIn(yaml, enabled)