import os
import types
import unittest
import shutil
import tempfile

from stado.core.site import Site


class TestSite(unittest.TestCase):
    """Base class for testing Site. Creates temporary directory."""

    def setUp(self):
        self.temp_path = tempfile.mkdtemp()
        path = os.path.dirname(__file__)
        self.site = Site(os.path.join(path, 'data'), self.temp_path)

    def tearDown(self):
        shutil.rmtree(self.temp_path)


class TestBuild(TestSite):
    """
    Site build() method:
    """
    pass


class TestRoute(TestSite):
    """
    Site route() method
    """

    def _check_route(self, path, source):
        """Checks files source and path."""

        path = os.path.join(self.site.output, path)
        self.assertTrue(os.path.exists(path))
        with open(path) as page:
            self.assertEqual(source, page.read())

    # Tests

    def test(self):
        """should create correct file with correct content"""

        self.site.route('/example.html', 'hello')
        self._check_route('example.html', 'hello')

    def test_function(self):
        """should use function as a argument"""

        def hello():
            return 'hello'

        self.site.route('/example.html', hello)
        self._check_route('example.html', 'hello')

    def test_index(self):
        """should add index.html to url without extension: / => /index.html"""

        self.site.route('/', 'hello')
        self._check_route('index.html', 'hello')
        self.site.route('/another', 'wow')
        self._check_route('another/index.html', 'wow')


class TestLoad(TestSite):
    """
    Site load() method
    """

    def test_load_file(self):
        """should return item if wildcards not used"""
        item = self.site.load('index.html')
        self.assertFalse(isinstance(item, list))
        self.assertEqual('index', item.source)

    def test_load_multiple_file(self):
        """should return list of items if wildcards used"""

        items = self.site.load('*.html')
        self.assertEqual(2, len(items))

        items = self.site.load('*.jpg')
        self.assertEqual(1, len(items))

        items = self.site.load('blog')
        self.assertEqual(3, len(items))


class TestFind(TestSite):
    """
    Site find() method
    """

    def test_find(self):
        """should yield items"""

        self.assertIsInstance(self.site.find('*'), types.GeneratorType)

        sources = [i.source for i in self.site.find('*.html')]
        self.assertCountEqual(['index', 'about'], sources)