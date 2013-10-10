import unittest
from stado.stado import Rendered

class TestRenderer(unittest.TestCase):

    def setUp(self):

        self.r = Rendered()


    # Simple rendering.

    def test_render_html(self):

        source, context = self.r.render(['html'], 'hello world')
        self.assertEqual(source, 'hello world')
        self.assertEqual(context, {})

    def test_render_json(self):

        source, context = self.r.render(['json'], '{"hello": "world"}')
        self.assertEqual(source, '{"hello": "world"}')
        self.assertEqual(context, {"hello": "world"})

    def test_render_yaml(self):

        source, context = self.r.render(['yaml'], 'hello: world')
        self.assertEqual(source, 'hello: world')
        self.assertEqual(context, {"hello": "world"})


    # Context.

    def test_render_with_context(self):

        source, context = self.r.render(['yaml'], 'hello: world', {'a': 1})
        self.assertEqual(source, 'hello: world')
        self.assertEqual(context, {"a": 1, "hello": "world"})



    # Chained rendering.

    def test_render_json_html(self):

        source, context = self.r.render(['json', 'html'], '{"hello": "world"}')
        self.assertEqual(source, '{"hello": "world"}')
        self.assertEqual(context, {"hello": "world"})