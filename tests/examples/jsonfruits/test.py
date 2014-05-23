"""Tests creating html page from json source using layout file."""

from tests.examples import TestExample


class TestJsonFruits(TestExample):
    """An example html page"""

    def test(self):
        """can be created from json source and layout file."""
        self.compare_outputs()