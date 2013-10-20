import os
from tests.plugins import TestPlugin


class TestPermalink(TestPlugin):

    def test_page(self):
        """Permalink plugins should correctly change page url."""

        # site.py

        self.app.permalink('page.html', '/b')
        self.app.run()

        # tests

        with open('b') as page:
            self.assertEqual('badger', page.read())


    def test_asset(self):
        """Permalink plugins should correctly change asset url."""

        # site.py

        self.app.permalink('image.jpg', '/test.jpg')
        self.app.run()

        # tests

        self.assertTrue(os.path.exists('test.jpg'))


    def test_keywords_path(self):
        """Permalink plugins should correctly change url using keywords."""

        # site.py

        self.app.permalink('page.html', '/:path/test.html')
        self.app.run()

        # tests

        self.assertTrue(os.path.exists('test.html'))

    def test_keywords_name(self):
        """Permalink plugins should correctly change url using keywords."""

        # site.py

        self.app.permalink('page.html', '/test/:name')
        self.app.run()

        # tests

        self.assertIn('page', os.listdir('test'))

    def test_keywords_filename(self):
        """Permalink plugins should correctly change url using keywords."""

        # site.py

        self.app.permalink('page.html', '/:filename')
        self.app.run()

        # tests

        self.assertIn('page.html', os.listdir())

    def test_keywords_extension(self):
        """Permalink plugins should correctly change url using keywords."""

        # site.py

        self.app.permalink('page.html', '/:extension')
        self.app.run()

        # tests

        self.assertIn('html', os.listdir())