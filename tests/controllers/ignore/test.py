import os
from tests.controllers import TestPlugin


class TestIgnore(TestPlugin):

    def test_path_argument(self):
        """Ignore plugin should correctly ignore files."""

        # site.py

        self.app.ignore('a.html')
        self.app.run()

        # tests

        self.assertNotIn('a.html', os.listdir())


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
        self.assertTrue(os.path.exists('_b'))


    def test_pattern_matching(self):
        """Ignore plugin should correctly ignore files using pattern matching."""

        # site.py

        self.app.ignore('*.html')
        self.app.run()

        # tests

        self.assertNotIn('a.html', os.listdir())
        self.assertNotIn('b.html', os.listdir())
        self.assertTrue(os.path.exists(os.path.join('b', 'b.html')))


    def test_pattern_matching_tree(self):
        """Ignore plugin should correctly ignore files using pattern matching with
        subdirectories."""

        # site.py

        self.app.ignore('b/*.html')
        self.app.run()

        # tests

        self.assertIn('a.html', os.listdir())
        self.assertFalse(os.path.exists(os.path.join('b', 'b.html')))


    def test_ignore_underscore_everywhere(self):

        # site.py

        self.app.ignore('**_*')
        self.app.run()

        # tests
        self.assertNotIn('_a.css', os.listdir())
        self.assertFalse(os.path.exists(os.path.join('_b', 'b.html')))
        self.assertFalse(os.path.exists(os.path.join('b', '_c.html')))

    def test_ignore_underscore_top(self):

        # site.py

        self.app.ignore('_*')
        self.app.run()

        # tests
        self.assertNotIn('_a.css', os.listdir())
        self.assertFalse(os.path.exists(os.path.join('_b', 'b.html')))
        self.assertTrue(os.path.exists(os.path.join('b', '_c.html')))
