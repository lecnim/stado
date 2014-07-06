from tests.plugins import TestPlugin


class TestYamlContext(TestPlugin):
    """
    Plugin yaml_context
    """

    def test_substitution(self):
        """should correctly load yaml data from file"""

        item = self.site.load('db.yaml')
        self.site.apply(item, 'yaml_context')

        self.assertEqual('hello world', item.context.get('msg'))