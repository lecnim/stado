import os
from stado import plugins
from tests.plugins import TestPlugin


class TestJsonContext(TestPlugin):
    """
    Plugin json_context
    """
    def setUp(self):
        super().setUp()
        self.plugin = plugins.load_plugin('json_context')()

    def test_substitution(self):
        """"""

        item = self.site.load('db.json')
        self.plugin.apply(item)
        self.assertEqual('hello world', item.context.get('msg'))