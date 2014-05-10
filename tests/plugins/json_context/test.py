from tests.plugins import TestPlugin


class TestJsonContext(TestPlugin):
    """
    Plugin json_context
    """

    def test_substitution(self):
        """"""

        item = self.site.load('db.json')
        self.site.apply(item, 'json_context')

        self.assertEqual('hello world', item.context.get('msg'))