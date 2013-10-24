import os
from tests.controllers import TestPlugin


class TestPermalink(TestPlugin):

    def test_page(self):
        """Permalink controllers should correctly change Content object url."""

        # site.py

        @self.app.before('page.html')
        def url(page):
            self.app.permalink(page, '/b')
        self.app.run()

        # tests

        with open('b') as page:
            self.assertEqual('badger', page.read())



    def test_page(self):
        """Permalink controllers should correctly change page url."""

        # site.py

        self.app.permalink('page.html', '/b')
        self.app.run()

        # tests

        with open('b') as page:
            self.assertEqual('badger', page.read())


    def test_asset(self):
        """Permalink controllers should correctly change asset url."""

        # site.py

        self.app.permalink('image.jpg', '/test.jpg')
        self.app.run()

        # tests

        self.assertTrue(os.path.exists('test.jpg'))


    def test_filename_matching(self):

        # site.py

        self.app.permalink('*.*', '/test/:path/:filename')
        self.app.run()

        # tests

        self.assertTrue(os.path.exists('test'))
        self.assertIn('image.jpg', os.listdir('test'))
        self.assertIn('page.html', os.listdir('test'))
        self.assertIn('a', os.listdir('test'))


    # Styles.

    def test_style_pretty(self):
        """Permalink controllers should correctly change url using built-in styles."""

        # site.py

        self.app.permalink('page.html', 'pretty')
        self.app.run()

        # tests

        self.assertTrue(os.path.exists('page'))
        self.assertIn('index.html', os.listdir('page'))

    def test_style_default(self):
        """Permalink controllers should correctly change url using built-in styles."""

        # site.py

        self.app.permalink('page.html', 'default')
        self.app.permalink('image.jpg', 'ugly')
        self.app.run()

        # tests

        self.assertTrue(os.path.exists('page.html'))
        self.assertTrue(os.path.exists('image.jpg'))


    # Keywords.

    def test_keywords_path(self):
        """Permalink controllers should correctly change url using keywords."""

        # site.py

        self.app.permalink('page.html', '/:path/test.html')
        self.app.run()

        # tests

        self.assertTrue(os.path.exists('test.html'))

    def test_keywords_name(self):
        """Permalink controllers should correctly change url using keywords."""

        # site.py

        self.app.permalink('page.html', '/test/:name')
        self.app.run()

        # tests

        self.assertTrue(os.path.exists('test'))
        self.assertIn('page', os.listdir('test'))

    def test_keywords_filename(self):
        """Permalink controllers should correctly change url using keywords."""

        # site.py

        self.app.permalink('page.html', '/:filename')
        self.app.run()

        # tests

        self.assertIn('page.html', os.listdir())

    def test_keywords_extension(self):
        """Permalink controllers should correctly change url using keywords."""

        # site.py

        self.app.permalink('page.html', '/:extension')
        self.app.run()

        # tests

        self.assertIn('html', os.listdir())
