"""
Building html page using json data and layout.
----------------------------------------------

All files that ends with 'md' or 'markdown' extension will
be auto built to html.
"""

from tests.examples import TestExample


class TestJsonFruits(TestExample):
    """An example html page"""

    def test(self):
        """can be created from json source and layout file."""
        self.compare_outputs()