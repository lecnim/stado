import unittest
from stado import templates


class TestMustacheTemplate(unittest.TestCase):
    """
    Tests Mustache template engine.
    """

    def test_render(self):
        """Stado should correctly render template using Mustache."""

        engine_class = templates.load('mustache')
        engine = engine_class()

        result = engine.render('{{ hello }}', {'hello': 'hello world'})
        self.assertEqual(result, 'hello world')
