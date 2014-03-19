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

    def compare_output(self, path, expected_source):
        path = os.path.join(self.site.output, path)
        self.assertTrue(os.path.exists(path))
        with open(path) as page:
            self.assertEqual(expected_source, page.read())


class TestBuild(TestSite):
    """
    Site build() method
    """

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

        class Hello:
            def apply(self, item):
                item.source = 'hello'

        self.site.build('index.html', Hello)
        self.compare_output('index.html', 'hello')

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


class TestInstall(TestSite):
    """
    Site install() method
    """

    def test_function(self):

        def plugin(item):
            item.source = 'wow'

        self.site.install('plugin', plugin)
        self.site.build('index.html', 'plugin')
        self.compare_output('index.html', 'wow')

    def test_class(self):

        class Plugin:
            def apply(self, item):
                item.source = 'wow'

        self.site.install('plugin', Plugin)
        self.site.build('index.html', 'plugin')
        self.compare_output('index.html', 'wow')

        # Test class instance.

        self.site.install('plugin2', Plugin())
        self.site.build('about.html', 'plugin2')
        self.compare_output('about.html', 'wow')


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
        """should return item if wildcards not used"""
        item = self.site.load('index.html')
        self.assertFalse(isinstance(item, list))
        self.assertEqual('index', item.source)
        self.assertEqual('index.html', item.output_path)

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