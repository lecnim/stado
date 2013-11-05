from tests.controllers import TestPlugin


class TestRenderFile(TestPlugin):

    def test_without_context(self):
        """Render plugin should correctly render given file."""

        # site.py

        x = self.app.render_file('a.html')

        # tests

        self.assertEqual('hello world', x)

    def test_with_context(self):
        """Render plugin should correctly render given file using context."""

        # site.py

        x = self.app.render_file('b.html', {'hello': 'hello world'})

        # tests

        self.assertEqual('hello world', x)
