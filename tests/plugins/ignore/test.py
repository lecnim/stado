import os
from tests.plugins import TestPlugin


class TestIgnore(TestPlugin):

    def test_path_argument(self):
        """Ignore plugin should correctly ignore files."""

        # site.py

        self.app.ignore('a.html')
        self.app.run()

        # tests

        self.assertNotIn('a.html', os.listdir())


    #def test_content_object(self):
    #    """Ignore plugin should correctly ignore files from Content object."""
    #
    #    # site.py
    #
    #    @self.app.before('a.html')
    #    def ignore_content(page):
    #        self.app.ignore(page)
    #    self.app.run()
    #
    #    # tests
    #
    #    self.assertNotIn('a.html', os.listdir())


    def test_multiple_path_arguments(self):
        """Ignore plugin should correctly ignore multiple files."""

        # site.py

        self.app.ignore('a.html', os.path.join('b', 'b.html'))
        self.app.run()

        # tests

        self.assertFalse(os.path.exists('a.html'))
        self.assertFalse(os.path.exists(os.path.join('b', 'b.html')))
        self.assertTrue(os.path.exists('b.html'))


    def test_dir(self):
        """Ignore plugin should correctly ignore directories."""

        # site.py

        self.app.ignore('b')
        self.app.run()

        # tests

        self.assertNotIn('b', os.listdir())
        self.assertTrue(os.path.exists('b.html'))


    def test_pattern_matching(self):
        """Ignore plugin should correctly ignore files using pattern matching."""

        # site.py

        self.app.ignore('*.html')
        self.app.run()

        # tests

        self.assertNotIn('a.html', os.listdir())
        self.assertFalse(os.path.exists(os.path.join('b', 'b.html')))


    def test_pattern_matching_tree(self):
        """Ignore plugin should correctly ignore files using pattern matching with
        subdirectories."""

        # site.py

        self.app.ignore('b/*.html')
        self.app.run()

        # tests

        self.assertIn('a.html', os.listdir())
        self.assertFalse(os.path.exists(os.path.join('b', 'b.html')))
