from tests.plugins import TestPlugin


class TestHelper(TestPlugin):

    def test_one_path(self):
        """Helper plugin should works correctly."""

        # site.py

        @self.app.helper
        def hello():
            return 'hello world'
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('hello world', page.read())


    def test_do_not_overwrite_context(self):
        """Helper plugin should not overwrite already existing context key."""

        # site.py

        @self.app.before('page.html')
        def page(path):
            return {'hello': 'hello world'}

        @self.app.helper
        def hello():
            return 'test'
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('hello world', page.read())
        with open('yaml.html') as page:
            self.assertEqual('hello: hello world\n', page.read())
        with open('json.html') as page:
            self.assertEqual('{"hello": "hello world"}', page.read())
