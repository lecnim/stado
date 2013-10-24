import os

from stado.core.content.loaders import FileSystemContentLoader
from stado.core.content.loaders import FileContent
from tests import TestInCurrentDirectory


class TestFileSystemContentLoader(TestInCurrentDirectory):
    """
    This test case change current working directory to __file__ location.
    """

    def test_returned_type(self):

        loader = FileSystemContentLoader()
        contents = [i for i in loader.load('data')]

        self.assertEqual(3, len(contents))
        self.assertIsInstance(contents[0], FileContent)


    def test_content_source(self):

        loader = FileSystemContentLoader()
        contents = [i for i in loader.load('data')]

        sources = [i.source for i in contents]
        self.assertCountEqual([os.path.join('data', 'a.html'),
                               os.path.join('data', 'b.html'),
                               os.path.join('data', 'b','b.md')], sources)


    def test_content_output(self):

        loader = FileSystemContentLoader()
        contents = [i for i in loader.load('data')]

        outputs = [i.output for i in contents]
        self.assertCountEqual([os.path.join('a.html'),
                               os.path.join('b.html'),
                               os.path.join('b','b.md')], outputs)


    def test_content_id(self):

        loader = FileSystemContentLoader()
        contents = [i for i in loader.load('data')]

        ids = [i.id for i in contents]
        self.assertCountEqual([os.path.join('a.html'),
                               os.path.join('b.html'),
                               os.path.join('b','b.md')], ids)


    def test_content_data(self):

        loader = FileSystemContentLoader()
        contents = [i for i in loader.load('data')]

        data = [i.data for i in contents]
        self.assertCountEqual(['a', 'b', 'bb'], data)
