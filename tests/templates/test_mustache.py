"""Testing support for Mustache."""

import unittest
from stado import templates


class TestMustacheTemplate(unittest.TestCase):
    """
    Template engine: Mustache
    """

    def test_render(self):
        """should correctly renders templates"""

        engine_class = templates.load('mustache')
        engine = engine_class()

        result = engine.render('{{ hello }}', {'hello': 'hello world'})
        self.assertEqual(result, 'hello world')
