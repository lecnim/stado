import os
import types

from stado import config
from stado.core.site import Site
from stado.core.item import SiteItem, FileItem, Item
from stado.plugins import Plugin
from tests import TestStado


class BaseTest(TestStado):
    """Base class for testing Site. Sites output is temporary directory."""

    def setUp(self):
        TestStado.setUp(self)
        self.site = Site(self.temp_path)


class TestSite(BaseTest):
    """Base class for testing Site. Sites output is temporary directory."""

    def setUp(self):
        TestStado.setUp(self)
        self.site = Site(self.temp_path)

    #

    def test_init(self):

        s = Site(self.temp_path, output='built')

        # Check properties:

        # source
        self.assertEqual(self.temp_path, s.path)
        # output
        self.assertEqual(os.path.abspath('built'), s.output)
        # ignore_paths
        self.assertEqual([os.path.abspath('built')], s.ignore_paths)


class TestBuild(BaseTest):
    """
    Site build() method
    """

    def test_utf8(self):
        """support utf8"""

        self.create_file('test.utf8', 'ąężółć')
        self.site.build('test.utf8')
        self.assertEqual('ąężółć', self.read_file('test.utf8'))

    def test_absolute_path(self):
        """should raise exception if path is absolute"""
        self.assertRaises(ValueError, self.site.build, '/blog/post.html')

    def test_path_not_found(self):
        """should raise exception if path is not found"""
        self.assertRaises(ValueError, self.site.build('not/found'))

    def test_all(self):
        """should build all site files if called without arguments"""

        self.create_file('a.html')
        self.create_file('a.txt')
        self.create_file('foo/bar')

        self.site.build()

        self.assertIn(config.build_dir, os.listdir('.'))
        self.assertCountEqual(['a.html', 'a.txt', 'foo'],
                              os.listdir(config.build_dir))

        # Do not include output directory.
        self.site.build()

        self.assertCountEqual(['a.html', 'a.txt', 'foo'],
                              os.listdir(config.build_dir))

        # Do not include parent script file.

        self.create_file('script.py')
        s = Site(self.temp_path, output='built')
        s._script_path = os.path.abspath('script.py')

        s.build()
        self.assertNotIn('script.py', os.listdir('built'))

    def test_build_parent_script(self):
        """can build parent python module"""

        self.create_file('script.py')
        self.site._script_path = os.path.abspath('script.py')
        self.site.build('script.py')
        self.assertEqual(['script.py'], os.listdir(config.build_dir))

    def test_build_file_in_output(self):
        """should raise exception if user want to build output file"""

        self.create_file('foo')
        self.site.build('foo')
        self.assertRaises(ValueError, self.site.build, config.build_dir + '/foo')

    def test_path(self):
        """should accept string as a path argument"""

        self.create_file('foo.html', 'bar')
        self.site.build('foo.html')
        self.assertEqual('bar', self.read_file(config.build_dir + '/foo.html'))

    def test_item(self):
        """should accept item object as a path argument"""

        # default

        self.create_file('foo.html', 'bar')

        page = self.site.load('foo.html')
        self.site.build(page)
        self.assertEqual('bar', self.read_file(config.build_dir + '/foo.html'))

        # FileItem

        self.create_file('cat.html', 'meow')

        i = FileItem('/dog.html', os.path.abspath('cat.html'))
        self.site.build(i)
        self.assertEqual('meow', self.read_file(config.build_dir + '/dog.html'))

        # Item

        i = Item('/foo', 'bar')
        self.site.build(i)
        self.assertEqual('bar', self.read_file(config.build_dir + '/foo'))

    def test_calling_function(self):
        """should accept function in plugins list"""

        self.create_file('foo.html', 'bar')

        def uppercase(item):
            item.source = item.source.upper()
            return item

        self.site.build('foo.html', uppercase)
        self.assertEqual('BAR', self.read_file(config.build_dir + '/foo.html'))

    def test_calling_class(self):
        """should accept class in plugins list"""

        self.create_file('foo.html', 'bar')

        class Hello(Plugin):
            def apply(self, site, item):
                item.source = 'hello'

        self.site.build('foo.html', Hello)
        self.assertEqual('hello', self.read_file(config.build_dir + '/foo.html'))

    def test_calling_instance(self):
        """should accept a plugin instance in the plugins list"""

        self.create_file('foo.html', 'bar')

        class Hello(Plugin):
            def apply(self, site, item):
                item.source = 'hello'

        self.site.build('foo.html', Hello())
        self.assertEqual('hello', self.read_file(config.build_dir + '/foo.html'))

    # context

    def test_context_restore(self):
        """should restore an items context after building it"""

        self.create_file('index.html', 'index')

        i = self.site.load('index.html')
        i.context['foo'] = 'hello world'
        self.site.build(i, context={'foo': 'bar'})

        self.assertEqual('hello world', i.context['foo'])

    # overwrite argument

    def test_not_overwrite(self):
        """should not overwrite already built items if overwrite=False"""

        self.create_file('foo.html', 'bar')

        def hello(item):
            item.source = 'OVER'

        self.site.build('foo.html', hello)
        self.site.build('foo.html', overwrite=False)
        self.assertEqual('OVER', self.read_file(config.build_dir + '/foo.html'))

        page = self.site.load('foo.html')
        self.site.build(page, overwrite=False)
        self.assertEqual('OVER', self.read_file(config.build_dir + '/foo.html'))
        
    def test_overwrite(self):
        """should overwrite already built items if overwrite=True"""

        self.create_file('foo.html', 'index')

        def hello(item):
            item.source = 'OVER'

        self.site.build('foo.html')
        self.site.build('foo.html', hello, overwrite=True)
        self.assertEqual('OVER', self.read_file(config.build_dir + '/foo.html'))


class TestRegister(BaseTest):
    """
    Site register() method
    """

    def test(self):

        self.create_file('index.html', 'index')

        def badger(item):
            item.source = 'badger!'

        self.site.register('**/*.html', badger)
        self.site.build('index.html')
        self.assertEqual('badger!',
                         self.read_file(config.build_dir + '/index.html'))


class TestRoute(BaseTest):
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

        self.site.route('/foo.html', 'bar')
        self.assertEqual('bar', self.read_file(config.build_dir + '/foo.html'))

    def test_function(self):
        """should use function as a argument"""

        def hello():
            return 'bar'

        self.site.route('/foo.html', hello)
        self.assertEqual('bar', self.read_file(config.build_dir + '/foo.html'))

    def test_index(self):
        """should add index.html to url without extension: / => /index.html"""

        self.site.route('/', 'bar')
        self.assertEqual('bar',
                         self.read_file(config.build_dir + '/index.html'))
        self.site.route('/wow', 'wow')
        self.assertEqual('wow',
                         self.read_file(config.build_dir + '/wow/index.html'))


class TestLoad(BaseTest):
    """
    Site load() method
    """

    def test_load_file(self):
        """should return one item if no wildcards used"""

        self.create_file('index.html')
        item = self.site.load('index.html')
        self.assertIsInstance(item, SiteItem)

    # exceptions

    def test_wildcards(self):
        """should raise error if wildcard is used"""

        self.assertRaises(ValueError, self.site.load, '*.html')

    def test_absolute_path(self):
        """should raise exception if path is absolute"""
        self.assertRaises(ValueError, self.site.load, '/blog/post.html')

    def test_directory(self):
        """should raise exception if path is directory"""
        self.create_dir('blog')
        self.assertRaises(ValueError, self.site.load, 'blog')

    def test_file_not_found(self):
        """should raise exception if file not found"""
        self.assertRaises(IOError, self.site.load, 'missing.html')

    # item attributes

    def test_item_output_path(self):
        """should set correct item output path (relative)"""
        self.create_file('index.html')
        item = self.site.load('index.html')
        self.assertEqual('index.html', item.output_path)

    def test_item_source_path(self):
        """should set correct item source path (absolute)"""
        self.create_file('index.html')
        item = self.site.load('index.html')
        self.assertEqual(os.path.abspath('index.html'), item.source_path)

    def test_item_source(self):
        """should set correct item source"""
        self.create_file('foo.html', 'bar')
        item = self.site.load('foo.html')
        self.assertEqual('bar', item.source)


class TestFind(BaseTest):
    """
    Site find() method
    """

    def test(self):
        """should yield items"""

        self.create_file('index.html', 'index')
        self.create_file('about.html', 'about')
        self.create_file('foo/bar.html', 'foobar')

        self.assertIsInstance(self.site.find('*'), types.GeneratorType)
        sources = [i.source for i in self.site.find('*.html')]
        self.assertCountEqual(['index', 'about'], sources)

    def test_results(self):
        """should yield correct amount of items"""

        self.create_file('a.html')
        self.create_file('b.html')
        self.create_file('img.jpg')
        self.create_file('blog/a.html')
        self.create_file('blog/b.html')

        items = [i for i in self.site.find('*.html')]
        self.assertEqual(2, len(items))

        items = [i for i in self.site.find('*.jpg')]
        self.assertEqual(1, len(items))

        items = [i for i in self.site.find('blog')]
        self.assertEqual(2, len(items))

    # exceptions

    def test_absolute_path(self):
        """should raise exception if path is absolute"""
        self.assertRaises(ValueError, lambda: [i for i in self.site.find('/')])

    # excluding

    def test_excluded_file(self):
        """should ignore files correctly"""

        # TODO: clean this mess!

        self.create_file('blog/old/ignore.html')

        self.site.ignore_paths = ['**/ignore.html']
        items = [i for i in self.site.find('blog/old/ignore.html')]
        self.assertEqual(0, len(items))

        self.site.ignore_paths = []
        items = [i for i in self.site.find('blog/old/ignore.html')]
        self.assertEqual(1, len(items))

    def test_excluded_directories(self):
        """should ignore directories correctly"""

        self.create_file('blog/foo.html', 'bar')

        # Relative path ignored.
        self.site.ignore_paths = ['blog']

        self.assertEqual(0, len([i for i in self.site.find('blog/*')]))
        self.assertEqual(0, len([i for i in self.site.find('blog/**')]))
        self.assertEqual(0, len([i for i in self.site.find('**/*.html')]))

        # Absolute path ignored.
        self.site.ignore_paths = [os.path.abspath('blog')]

        self.assertEqual(0, len([i for i in self.site.find('blog/*')]))
        self.assertEqual(0, len([i for i in self.site.find('blog/**')]))
        self.assertEqual(0, len([i for i in self.site.find('**/*.html')]))


class TestHelper(BaseTest):
    """
    Site helper() method
    """

    def test_removing(self):
        """should remove helpers after building"""

        @self.site.helper
        def hello():
            return 'hello world'

        i = Item('/foo', '{{ hello }}')
        self.site.build(i, 'mustache')
        self.assertFalse('hello' in i.context)

    def test_context(self):
        """should correctly works with custom context argument in build"""

        @self.site.helper
        def hello():
            return 'hello world'

        i = Item('/foo', '{{ hello }}')
        self.site.build(i, 'mustache', context={'a': 1})
        self.assertEqual('hello world', self.read_file(config.build_dir + '/foo'))

    def test_context_overwrite(self):
        """should not overwrite custom context argument in build"""

        @self.site.helper
        def hello():
            return 'hello world'

        i = Item('/foo', '{{ hello }}')
        self.site.build(i, 'mustache', context={'hello': 'bar'})
        self.assertEqual('bar', self.read_file(config.build_dir + '/foo'))

    # Test types.

    def test_str(self):
        """should works correctly if string returned"""

        @self.site.helper
        def hello():
            return 'hello world'

        i = Item('/foo', '{{ hello }}')
        self.site.build(i, 'mustache')
        self.assertEqual('hello world', self.read_file(config.build_dir + '/foo'))

    def test_list(self):
        """should works correctly if list returned"""

        @self.site.helper
        def test():
            return [1, 2, 3]

        i = Item('/foo', '{{# test }}{{.}}{{/ test }}')
        self.site.build(i, 'mustache')
        self.assertEqual('123', self.read_file(config.build_dir + '/foo'))

    def test_list_of_dict(self):
        """should works correctly if list of dict returned"""

        @self.site.helper
        def test():
            return [{'a': 1}, {'a': 2}, {'a':3}]

        i = Item('/foo', '{{# test }}{{a}}{{/ test }}')
        self.site.build(i, 'mustache')
        self.assertEqual('123', self.read_file(config.build_dir + '/foo'))

    def test_dict(self):
        """should works correctly if dict returned"""

        @self.site.helper
        def test():
            return {'key': 'value'}

        i = Item('/foo', '{{ test.key }}')
        self.site.build(i, 'mustache')
        self.assertEqual('value', self.read_file(config.build_dir + '/foo'))

    # Other tests.

    def test_do_not_overwrite_context(self):
        """should not overwrite already existing context key"""

        i = Item('/foo', '{{ foo }}')
        i.context['foo'] = 'bar'

        @self.site.helper
        def foo():
            return 'helpers rulezz'

        self.site.build(i, 'mustache')
        self.assertEqual('bar', self.read_file(config.build_dir + '/foo'))

del BaseTest