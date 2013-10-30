import unittest
from stado.core.pathmatch import pathmatch


class TestPathMatch(unittest.TestCase):

    def test_file(self):

        self.assertTrue(pathmatch('a.html', 'a.html'))
        self.assertTrue(pathmatch('b/a.html', 'b/a.html'))
        self.assertTrue(pathmatch('b\\a.html', 'b/a.html'))
        self.assertTrue(pathmatch('b/a.html', 'b\\a.html'))

        self.assertFalse(pathmatch('b/a.html', '/b/a.html'))
        self.assertFalse(pathmatch('b\\a.html', '\\b\\a.html'))


    def test_directory(self):

        self.assertTrue(pathmatch('a', 'a'))
        self.assertTrue(pathmatch('b/a', 'b/a'))
        self.assertTrue(pathmatch('b\\a', 'b/a'))
        self.assertTrue(pathmatch('b/a', 'b\\a'))

        self.assertFalse(pathmatch('b/a', '/b/a'))
        self.assertFalse(pathmatch('b\\a', '\\b\\a'))


    def test_any_file(self):

        self.assertTrue(pathmatch('a.html', '*'))
        self.assertTrue(pathmatch('abc.html', '*'))
        self.assertTrue(pathmatch('a/a.html', '*/*'))
        self.assertTrue(pathmatch('a\\a.html', '*\\*'))
        self.assertTrue(pathmatch('a/abc.html', '*/*'))
        self.assertTrue(pathmatch('a/abc.html', '*\\*'))
        self.assertTrue(pathmatch('a\\abc.html', '*/*'))

        self.assertFalse(pathmatch('a/a.html', '*'))
        self.assertFalse(pathmatch('a\\a.html', '*'))


    def test_file_endswith(self):

        self.assertTrue(pathmatch('a.html', '*.html'))
        self.assertTrue(pathmatch('abc.html', '*c.html'))
        self.assertTrue(pathmatch('a/a.html', '*/*l'))
        self.assertTrue(pathmatch('a/abc.html', '*/*l'))

        self.assertFalse(pathmatch('a/a.html', '*.html'))
        self.assertFalse(pathmatch('a\\a.html', '*.html'))

    def test_everything(self):

        self.assertTrue(pathmatch('a', '**'))
        self.assertTrue(pathmatch('abc.html', '**'))
        self.assertTrue(pathmatch('a/a', '**'))
        self.assertTrue(pathmatch('a/a/b', '**/b'))
        self.assertTrue(pathmatch('a\\a\\b', '**\\b'))
        self.assertTrue(pathmatch('a/a/b.html', '**b.html'))
        self.assertTrue(pathmatch('b.html', '**b.html'))
        self.assertTrue(pathmatch('bb.html', '**b.html'))
        self.assertTrue(pathmatch('a/a/ab.html', '**b.html'))
