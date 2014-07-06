import os
from tests.plugins import TestPlugin


class TestHtml(TestPlugin):
    """
    Plugin html
    """

    def test_substitution(self):
        """should change items output file extension to html"""

        self.site.build('index.md', 'html')
        # Check if file exists in output directory.
        self.assertTrue(os.path.exists('index.html'))