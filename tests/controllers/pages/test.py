from tests.controllers import TestPlugin


class TestPages(TestPlugin):

    def test(self):
        """Pages plugin should correctly yields pages from path."""

        # site.py

        @self.app.before('*')
        def set_title(page):
            return {'title': 'badger'}

        @self.app.helper
        def pages():
            return [i for i in self.app.pages('*')]
        self.app.run()

        # tests

        with open('page.html') as file:
            self.assertEqual("badger\nbadger\nbadger\n", file.read())
