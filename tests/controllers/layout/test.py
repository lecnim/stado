import os
from tests.controllers import TestPlugin


class TestLayout(TestPlugin):

    def test_str(self):
        """Layout plugin should render page template using given layout."""

        # site.py

        self.app.layout('page.html', 'layout.html')
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('layout badger', page.read())


    def test_content_object(self):
        """Layout plugin should accept Content objects as a argument."""

        # site.py

        page = self.app.get('page.html')
        self.app.layout(page, 'layout.html')

        # tests

        self.assertIn('layout.html', page.layouts[0],
                      'Layout controller should change item layout directly after '
                      'calling in other controllers.')

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


    def test_default_layout(self):
        """Layout plugin should render all pages without layouts using
        default layout. Heh it sounds weird."""

        # site.py

        self.app.layout('layout.html')
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('layout badger', page.read())
        with open('markdown.html') as page:
            self.assertEqual('layout <p>badger</p>', page.read())

        self.assertFalse(os.path.exists('layout.html'))


    def test_context(self):
        """Layout plugin should correctly use own context."""

        # site.py

        self.app.context('page.html', {'title': 'page'})
        self.app.layout('page.html', 'context-layout.html', 'layout.html',
                        context={'title': 'title'})
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('layout title page badger', page.read())


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

        self.app.layout('*', 'layout.html')
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('layout badger', page.read())
        with open('markdown.html') as page:
            self.assertEqual('layout <p>badger</p>', page.read())
