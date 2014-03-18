import os
from tests.controllers import TestPlugin


class TestPermalink(TestPlugin):

    def test_item(self):
        """Permalink controllers should correctly change Item object url."""

        # site.py

        page = self.app.get('page.html')
        self.app.permalink(page, '/b')
        self.assertEqual('/b', page.permalink, "should modify item.url after calling")
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

        self.app.permalink('**', '/test/:path/:filename')
        self.app.run()

        # tests

        self.assertTrue(os.path.exists('test'))
        self.assertIn('image.jpg', os.listdir('test'))
        self.assertIn('page.html', os.listdir('test'))
        self.assertIn('a', os.listdir('test'))


    def test_default_permalink(self):
        """Calling permalink controller with only on argument should change url of
        all page items."""

        # site.py

        self.app.permalink('/test/:path/:filename')
        self.app.run()

        # tests

        self.assertTrue(os.path.exists('test'))
        self.assertNotIn('image.jpg', os.listdir('test'))
        self.assertIn('page.html', os.listdir('test'))
        self.assertIn('a', os.listdir('test'))
        self.assertTrue(os.path.exists(os.path.join('test', 'a', 'page.html')))



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

    def test_item_style_pretty(self):
        """Permalink controllers should correctly change url using built-in styles."""

        # site.py

        page = self.app.get('page.html')
        self.app.permalink(page, 'pretty')
        self.app.run()

        # tests

        self.assertTrue(os.path.exists('page'))
        self.assertIn('index.html', os.listdir('page'))


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
