from stado import plugins
from tests.plugins import TestPlugin


class TestMarkdown(TestPlugin):
    """
    Plugin markdown
    """
    def setUp(self):
        super().setUp()
        self.plugin = plugins.load_plugin('markdown')(self.site)

    # plugin module

    def test_apply(self):
        """should correctly convert item markdown source to html"""

        item = self.site.load('page.md')
        self.plugin.apply(self.site, item)

        self.assertEqual('<h1>header</h1>', item.source)