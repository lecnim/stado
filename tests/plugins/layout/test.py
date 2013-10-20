import os
from tests.plugins import TestPlugin


class TestLayout(TestPlugin):

    def test(self):
        """Layout plugin should render page template using given layout."""

        # site.py

        self.app.layout('page.html', 'layout.html')
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('layout badger', page.read())


    def test_multiple_layouts(self):
        """Layout plugin should render page template using multiple layouts."""

        # site.py

        self.app.layout('page.html', 'sub-layout.html', 'layout.html')
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('layout sub-layout badger', page.read())


    def test_ignore_layouts(self):
        """Layout plugin should prevent layout files in output."""

        # site.py

        self.app.layout('page.html', 'layout.html')
        self.app.run()

        # tests

        self.assertFalse(os.path.exists('layout.html'))


    def test_filename_matching(self):
        """Layout plugin should render page template using multiple layouts."""

        # site.py

        self.app.layout('*.*', 'layout.html')
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('layout badger', page.read())
        with open('markdown.html') as page:
            self.assertEqual('layout <p>badger</p>', page.read())
