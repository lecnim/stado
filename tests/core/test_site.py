import os
import types

from stado.core.site import Site
from tests import TestTemporaryDirectory


class TestSite(TestTemporaryDirectory):

    def setUp(self):
        TestTemporaryDirectory.setUp(self)

        path = os.path.dirname(__file__)
        self.site = Site(os.path.join(path, 'data'), self.temp_path)

    # route

    def check_route(self, path, source):

        path = os.path.join(self.site.output, path)
        self.assertTrue(os.path.exists(path))
        with open(path) as page:
            self.assertEqual(source, page.read())

    def test_route(self):

        self.site.route('/example.html', 'hello')
        self.check_route('example.html', 'hello')

    def test_route_function(self):
        """route() should support function as a argument"""

        def hello():
            return 'hello'

        self.site.route('/example.html', hello)
        self.check_route('example.html', 'hello')

    def test_route_dir(self):

        self.site.route('/', 'hello')
        self.check_route('index.html', 'hello')
        self.site.route('/another', 'wow')
        self.check_route('another/index.html', 'wow')

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

        sources = [i.source for i in self.site.find('*.html')]
        self.assertCountEqual(['index', 'about'], sources)
