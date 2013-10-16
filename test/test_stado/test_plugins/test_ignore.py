import unittest
import os
from test.test_stado.test_plugins import TestPlugin
from stado import Stado


class TestIgnore(TestPlugin):

    def setUp(self):
        TestPlugin.setUp(self)

        self.app = Stado(os.path.join(self.path, 'test_ignore'))
        self.app.destination = self.temp_path


    def test_file(self):
        """Ignore plugin should correctly ignore files."""

        self.app.ignore('a.html')
        self.app.run()

        self.assertNotIn('a.html', os.listdir(self.temp_path))

    def test_multiple_files(self):
        """Ignore plugin should correctly ignore multiple files."""

        self.app.ignore('a.html', os.path.join('b', 'b.html'))
        self.app.run()

        self.assertFalse(os.path.exists(os.path.join(self.temp_path, 'a.html')))
        self.assertFalse(os.path.exists(os.path.join(self.temp_path, 'b', 'b.html')))

    @unittest.skip
    def test_dir(self):
        """Ignore plugin should correctly ignore directories."""

        self.app.ignore('b')
        self.app.run()

        self.assertNotIn('b', os.listdir(self.temp_path))


    def test_pattern_matching(self):
        """Ignore plugin should correctly ignore files using pattern matching."""

        self.app.ignore('*.html')
        self.app.run()

        self.assertNotIn('a.html', os.listdir(self.temp_path))
        self.assertFalse(os.path.exists(os.path.join(self.temp_path, 'b', 'b.html')))

    def test_pattern_matching_tree(self):
        """Ignore plugin should correctly ignore files using pattern matching with
        subdirectories."""

        self.app.ignore('b/*.html')
        self.app.run()

        self.assertIn('a.html', os.listdir(self.temp_path))
        self.assertFalse(os.path.exists(os.path.join(self.temp_path, 'b', 'b.html')))
