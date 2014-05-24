import os
import tempfile
import shutil

from tests import TestInCurrentDirectory
from stado.core.item import SiteItem, FileItem, Item


class TestFileItem(TestInCurrentDirectory):
    """FileItem class"""

    def test_attributes(self):
        """should create object with correct attributes"""

        i = FileItem('/foo', 'data/index.html')
        self.assertEqual('index', i.source)
        self.assertEqual('foo', i.output_path)


class TestItem(TestInCurrentDirectory):
    """Item class"""

    def test_attributes(self):
        """should create object with correct attributes"""

        i = Item('/foo', 'hello world')
        self.assertIsNone(i.source_path)
        self.assertEqual('hello world', i.source)
        self.assertEqual('foo', i.output_path)

    def test_match(self):
        """should not be matched by glob"""

        i = Item('/foo')
        self.assertFalse(i.match('*'))


class TestSiteItem(TestInCurrentDirectory):
    """
    SiteItem class
    """

    # deploy()

    def test_deploy_modified(self):
        """should write modified item source to output file"""

        t = tempfile.mkdtemp()

        item = SiteItem('data/index.html', 'foo')
        item.source = 'hello world'
        item.deploy(t)
        with open(os.path.join(t, 'foo')) as file:
            self.assertEqual('hello world', file.read())

        shutil.rmtree(t)

    def test_deploy_unmodified(self):
        """should copy source file to output directory if source not modified"""

        t = tempfile.mkdtemp()

        SiteItem('data/index.html', 'foo').deploy(t)
        with open(os.path.join(t, 'foo')) as file:
            self.assertEqual('index', file.read())

        shutil.rmtree(t)

    def test_deploy_missing_directory(self):
        """should create missing directories before writing to output"""

        t = tempfile.mkdtemp()

        SiteItem('data/index.html', 'a/b/c/foo').deploy(t)
        with open(os.path.join(t, 'a', 'b', 'c', 'foo')) as file:
            self.assertEqual('index', file.read())

        shutil.rmtree(t)

    # match()

    def test_match(self):
        """match()"""

        i = SiteItem('/index.html', 'item.html')

        self.assertTrue(i.match('/index.html'))
        self.assertTrue(i.match('/index.*'))
        self.assertFalse(i.match('/example.html'))

    # url

    def test_url_styles(self):
        """should change url using built-in styles"""

        i = SiteItem(None, 'item.html')

        # pretty-html

        i.url = 'pretty-html'
        self.assertEqual('/item/index.html', i.url)

        # pretty-html: prevent 'index.html' => 'index/index.html'
        x = SiteItem(None, 'index.html')
        x.url = 'pretty-html'
        self.assertEqual('/index.html', x.url)

        # default

        i.url = 'default'
        self.assertEqual('/item.html', i.url)

    def test_url_keywords(self):
        """should change url using keywords"""

        i = SiteItem(None, 'item.html')

        # path

        i.url = '/:path/foo'
        self.assertEqual('/foo', i.url)

        y = SiteItem('/blog/post.md', 'blog/post.md')
        y.url = '/:path/foo'
        self.assertEqual('/blog/foo', y.url)

        # name

        i.url = '/:name'
        self.assertEqual('/item', i.url)

        # filename

        i.url = '/:filename'
        self.assertEqual('/item.html', i.url)

        # extension

        i.url = '/:extension'
        self.assertEqual('/html', i.url)