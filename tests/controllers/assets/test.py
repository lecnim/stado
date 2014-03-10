from tests.controllers import TestPlugin


class TestAssets(TestPlugin):

    def test(self):
        """Pages plugin should correctly yields pages from path."""

        # site.py

        self.app.context('**.jpg', {'title': 'badger'})

        # @self.app.before('**.jpg')
        # def set_title(page):
        #     return {'title': 'badger'}

        @self.app.helper
        def assets():
            return [i for i in self.app.assets('**')]
        self.app.run()

        # tests

        with open('page.html') as file:
            self.assertEqual("badger\nbadger\nbadger\n", file.read())
