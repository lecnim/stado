import unittest
import os


@unittest.skip
class TestRenderer(unittest.TestCase):

    def setUp(self):

        self.path = os.path.join(os.path.dirname(__file__), 'data')
        self.r = Rendered(self.path)


    # Simple rendering.

    def test_render_without_context(self):

        data = self.r.render('hello world')
        self.assertEqual(data, 'hello world')

    def test_render_with_context(self):

        data = self.r.render('{{ hello }}', {'hello': 'hello world'})
        self.assertEqual(data, 'hello world')
