import os
import types
import unittest
import shutil
import tempfile

from stado.core.site import Site
from stado.core.item import SiteItem
from stado.plugins import Plugin


class TestSite(unittest.TestCase):
    """Base class for testing Site. Sites output is temporary directory."""

    def setUp(self):
        self.temp_path = tempfile.mkdtemp()
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        self.site = Site(self.data_path, self.temp_path)

    def tearDown(self):
        shutil.rmtree(self.temp_path)

    def compare_output(self, path, expected_source):
        path = os.path.join(self.site.output, path)
        self.assertTrue(os.path.exists(path))
        with open(path) as page:
            self.assertEqual(expected_source, page.read())


class TestBuild(TestSite):
    """
    Site build() method
    """

    # exceptions

    def test_absolute_path(self):
        """should raise exception if path is absolute"""
        self.assertRaises(ValueError, self.site.build, '/blog/post.html')

    # path argument

    def test_all(self):
        """should build all site files by default"""

        self.site.build()
        f = []
        for i in os.walk(self.temp_path):
            f.extend(i[2])
        self.assertEqual(8, len(f))

    def test_path(self):
        """should accept string as a path argument"""

        self.site.build('index.html')
        self.compare_output('index.html', 'index')

    def test_item(self):
        """should accept item object as a path argument"""

        page = self.site.load('index.html')
        self.site.build(page)
        self.compare_output('index.html', 'index')

    def test_calling_function(self):
        """should accept function in plugins list"""

        def uppercase(item):
            item.source = item.source.upper()
            return item

        self.site.build('index.html', uppercase)
        self.compare_output('index.html', 'INDEX')

    def test_calling_class(self):
        """should accept class in plugins list"""

        class Hello(Plugin):
            def apply(self, item):
                item.source = 'hello'

        self.site.build('index.html', Hello)
        self.compare_output('index.html', 'hello')

    def test_calling_instance(self):
        """should accept plugin instance in plugins list"""

        class Hello(Plugin):
            def apply(self, item):
                item.source = 'hello'

        self.site.build('index.html', Hello())
        self.compare_output('index.html', 'hello')

    # overwrite argument

    def test_not_overwrite(self):
        """should not overwrite already built items if overwrite=False"""

        def hello(item):
            item.source = 'overwritten'

        self.site.build('index.html', hello)
        self.site.build('index.html', overwrite=False)
        self.compare_output('index.html', 'overwritten')

        page = self.site.load('index.html')
        self.site.build(page, overwrite=False)
        self.compare_output('index.html', 'overwritten')

    def test_overwrite(self):
        """should overwrite already built items if overwrite=True"""

        def hello(item):
            item.source = 'overwritten'

        self.site.build('index.html')
        self.site.build('index.html', hello, overwrite=True)
        self.compare_output('index.html', 'overwritten')


class TestRegister(TestSite):
    """
    Site register() method
    """

    def test(self):

        def badger(item):
            item.source = 'badger!'

        self.site.register('**/*.html', badger)
        self.site.build('index.html')
        self.compare_output('index.html', 'badger!')


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
        self.compare_output('example.html', 'hello')

    def test_function(self):
        """should use function as a argument"""

        def hello():
            return 'hello'

        self.site.route('/example.html', hello)
        self.compare_output('example.html', 'hello')

    def test_index(self):
        """should add index.html to url without extension: / => /index.html"""

        self.site.route('/', 'hello')
        self.compare_output('index.html', 'hello')
        self.site.route('/another', 'wow')
        self.compare_output('another/index.html', 'wow')


class TestLoad(TestSite):
    """
    Site load() method
    """

    def test_load_file(self):
        """should return one item if no wildcards used"""

        item = self.site.load('index.html')
        self.assertIsInstance(item, SiteItem)

    def test_load_multiple_files(self):
        """should return list of items if wildcards used"""

        items = self.site.load('*.html')
        self.assertEqual(2, len(items))

        items = self.site.load('*.jpg')
        self.assertEqual(1, len(items))

        items = self.site.load('blog')
        self.assertEqual(3, len(items))

    # exceptions

    def test_absolute_path(self):
        """should raise exception if path is absolute"""
        self.assertRaises(ValueError, self.site.load, '/blog/post.html')

    # item attributes

    def test_item_output_path(self):
        """should set correct item output path (relative)"""
        item = self.site.load('index.html')
        self.assertEqual('index.html', item.output_path)

    def test_item_source_path(self):
        """should set correct item source path (absolute)"""
        item = self.site.load('index.html')
        self.assertEqual(os.path.join(self.data_path, 'index.html'),
                         item.source_path)

    def test_item_source(self):
        """should set correct item source"""
        item = self.site.load('index.html')
        self.assertEqual('index', item.source)


class TestFind(TestSite):
    """
    Site find() method
    """

    def test(self):
        """should yield items"""

        self.assertIsInstance(self.site.find('*'), types.GeneratorType)
        sources = [i.source for i in self.site.find('*.html')]
        self.assertCountEqual(['index', 'about'], sources)

    # exceptions

    def test_absolute_path(self):
        """should raise exception if path is absolute"""
        self.assertRaises(ValueError, lambda: [i for i in self.site.find('/')])

    # excluding

    def test_excluded_file(self):
        """should ignore files correctly"""

        self.site.excluded_paths = ['**/ignore.html']
        items = [i for i in self.site.find('blog/old/ignore.html')]
        self.assertEqual(0, len(items))

    def test_excluded_directories(self):
        """should ignore directories correctly"""

        self.site.excluded_paths = ['blog']
        items = [i for i in self.site.find('blog/*')]
        self.assertEqual(0, len(items))