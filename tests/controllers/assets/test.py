from tests.controllers import TestPlugin


class TestAssets(TestPlugin):

    def test(self):
        """Pages plugin should correctly yields pages from path."""

        # site.py

        @self.app.before('*.jpg')
        def set_title(page):
            print(page.source)
            return {'title': 'badger'}

        @self.app.helper
        def assets():
            print([i.metadata for i in self.app.assets('*')])
            return [i for i in self.app.assets('*')]
        self.app.run()

        # tests

        with open('page.html') as file:
            self.assertEqual("badger\nbadger\nbadger\n", file.read())
