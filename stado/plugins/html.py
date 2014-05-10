"""
Plugin sets item output file extension to html.
For example: 'page.md' => 'page.html'
"""

import os
from . import Plugin


class Html(Plugin):
    """
    Plugin html.
    """

    @staticmethod
    def apply(item):
        """Sets item output file extension to html."""

        base_path = os.path.splitext(item.url)[0]
        item.url = base_path + '.html'
