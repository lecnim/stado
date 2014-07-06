"""
Support for restructured text.
"""

from . import Plugin

try:
    from docutils.core import publish_string, publish_parts
except ImportError:
    raise ImportError('Require docutils module!')


# Template engine class.

class Rest(Plugin):
    """Wrapper for jinja2 module."""

    def apply(self, site, item):
        """Renders source with given context and apply to item."""

        html = publish_parts(item.source, writer_name='html')['html_body']
        item.source = html