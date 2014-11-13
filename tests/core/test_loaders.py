import os

from stado.core.loaders import FileLoader
from stado.core.item import SiteItem
from tests import BaseTest


class TestFileLoader(BaseTest):
    """
    A FileLoader
    """

    def test_returned_type(self):
        """should yield correct item type"""

        self.create_file('data/a.file')

        loader = FileLoader()
        contents = [i for i in loader.load('data')]

        self.assertEqual(1, len(contents))
        self.assertIsInstance(contents[0], SiteItem)

    def test_yield_items(self):
        """should yield correct items"""

        self.create_file('data/a.file', 'a')
        self.create_file('data/b.file', 'b')
        self.create_file('data/b/a.file' , 'ba')

        # output_paths

        items = [i for i in FileLoader().load('data')]
        generated_outputs = [i.output_path for i in items]
        outputs = [os.path.join('data', 'a.file'),
                   os.path.join('data', 'b.file'),
                   os.path.join('data', 'b', 'a.file')]

        self.assertCountEqual(outputs, generated_outputs)

        # source_paths

        generated_sources = [i.source_path for i in items]
        sources = [os.path.join('data', 'a.file'),
                   os.path.join('data', 'b.file'),
                   os.path.join('data', 'b', 'a.file')]

        self.assertCountEqual(sources, generated_sources)

        # sources

        sources = [i.source for i in items]
        self.assertCountEqual(['a', 'b', 'ba'], sources)