"""Tests auto building markdown files to html."""

from tests.examples import TestExample


class TestMarkdownToHtml(TestExample):
    """An example markdown file"""

    def test(self):
        """should be auto converted to html"""
        self.compare_outputs()