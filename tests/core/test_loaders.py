import os

from stado.core.loaders import FileSystemItemLoader
from stado.core.loaders import FileItem
from tests import TestInCurrentDirectory


class TestFileSystemContentLoader(TestInCurrentDirectory):
    """
    This test case change current working directory to __file__ location.
    """

    def test_returned_type(self):

        loader = FileSystemItemLoader()
        contents = [i for i in loader.load('data')]

        self.assertEqual(4, len(contents))
        self.assertIsInstance(contents[0], FileItem)


    def test_content_source(self):

        loader = FileSystemItemLoader()
        contents = [i for i in loader.load('data')]

        sources = [i.source for i in contents]
        self.assertCountEqual(['a.html', 'b.html', 'image.jpg',
                               os.path.join('b','b.md')], sources)


    def test_content_output(self):

        loader = FileSystemItemLoader()
        contents = [i for i in loader.load('data')]

        outputs = [i.output for i in contents]
        self.assertCountEqual([os.path.join('a.html'),
                               os.path.join('b.html'),
                               os.path.join('image.jpg'),
                               os.path.join('b','b.md')], outputs)


    def test_content_path(self):

        loader = FileSystemItemLoader()
        contents = [i for i in loader.load('data')]

        paths = [i.path for i in contents]
        self.assertCountEqual([os.path.join('data', 'a.html'),
                               os.path.join('data', 'b.html'),
                               os.path.join('data', 'image.jpg'),
                               os.path.join('data', 'b','b.md')], paths)


    def test_content_data(self):

        loader = FileSystemItemLoader()
        contents = [i for i in loader.load('data')]

        data = [i.data for i in contents if i.source.endswith('.html')]
        self.assertCountEqual(['a', 'b'], data)
