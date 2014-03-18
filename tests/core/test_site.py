import os
import types

from stado.core.site import Site
from tests import TestTemporaryDirectory


class TestSite(TestTemporaryDirectory):

    def setUp(self):
        TestTemporaryDirectory.setUp(self)

        path = os.path.dirname(__file__)
        self.site = Site(os.path.join(path, 'data'), self.temp_path)

    # load

    def test_load_file(self):
        """load() method should return item if wildcards not used"""
        item = self.site.load('index.html')
        self.assertFalse(isinstance(item, list))
        self.assertEqual('index', item.source)

    def test_load_multiple_file(self):
        """load() method should return list of items if wildcards used"""

        items = self.site.load('*.html')
        self.assertEqual(2, len(items))

        items = self.site.load('*.jpg')
        self.assertEqual(1, len(items))

        items = self.site.load('blog')
        self.assertEqual(3, len(items))

    # find

    def test_find(self):
        """find() method should yield items"""

        self.assertIsInstance(self.site.find('*'), types.GeneratorType)
