import os

from stado.core.loaders import FileLoader
from stado.core.loaders import FileItem
from tests import TestInCurrentDirectory


class TestFileLoader(TestInCurrentDirectory):
    """
    A FileLoader

    This test case change current working directory to __file__ location.
    """

    def test_returned_type(self):
        """should return correct item type"""

        loader = FileLoader()
        contents = [i for i in loader.load('data')]

        self.assertEqual(8, len(contents))
        self.assertIsInstance(contents[0], FileItem)

    # TODO:
    # def test_content_source(self):
    #
    #     loader = FileLoader()
    #     contents = [i for i in loader.load('data')]
    #
    #     sources = [i.id for i in contents]
    #     self.assertCountEqual(['a.html', 'b.html', 'image.jpg', 'b/b.md'],
    #                           sources)


    def test_item_output_path(self):
        """should generated correct item output path"""

        items = [i for i in FileLoader().load('data')]
        generated_outputs = [i.output_path for i in items]
        outputs = [os.path.join('index.html'),
                   os.path.join('about.html'),
                   os.path.join('image.jpg'),
                   os.path.join('blog', 'post.md'),
                   os.path.join('blog', 'post.html'),
                   os.path.join('blog', 'old', 'ignore.html'),
                   os.path.join('blog2', 'post.html'),
                   os.path.join('blog2', 'post.mustache')]

        self.assertCountEqual(outputs, generated_outputs)

    def test_item_source_path(self):
        """should generated correct item source path"""

        items = [i for i in FileLoader().load('data')]
        generated_sources = [i.source_path for i in items]
        sources = [os.path.join('data', 'index.html'),
                   os.path.join('data', 'about.html'),
                   os.path.join('data', 'image.jpg'),
                   os.path.join('data', 'blog', 'post.md'),
                   os.path.join('data', 'blog', 'post.html'),
                   os.path.join('data', 'blog', 'old', 'ignore.html'),
                   os.path.join('data', 'blog2', 'post.html'),
                   os.path.join('data', 'blog2', 'post.mustache')]

        self.assertCountEqual(sources, generated_sources)

    def test_item_source(self):
        """should generated correct item source"""

        items = [i for i in FileLoader().load('data/*.html')]
        sources = [i.source for i in items]
        self.assertCountEqual(['index', 'about'], sources)