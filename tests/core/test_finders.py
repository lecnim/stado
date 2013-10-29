import os

from stado.core.finders import FileSystemItemFinder
from tests import TestInCurrentDirectory


class TestFileSystemContentFinder(TestInCurrentDirectory):
    """
    This test case change current working directory to __file__ location.
    """

    def test_search(self):

        finder = FileSystemItemFinder()
        files = [i for i in finder.search('data')]

        self.assertEqual(4, len(files))
        self.assertIn(os.path.join('data', 'a.html'), files)
        self.assertIn(os.path.join('data', 'b.html'), files)
        self.assertIn(os.path.join('data', 'image.jpg'), files)
        self.assertIn(os.path.join('data', 'b', 'b.md'), files)


    def test_search_excluded_dirs(self):

        finder = FileSystemItemFinder()
        files = [i for i in finder.search('data', excluded_paths=['b'])]

        self.assertEqual(3, len(files))


    def test_search_excluded_files(self):

        finder = FileSystemItemFinder()
        files = [i for i in finder.search('data', excluded_paths=['a.html'])]

        self.assertEqual(3, len(files))
