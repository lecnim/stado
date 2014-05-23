import unittest
from stado.core.item import SiteItem


class TestSiteItem(unittest.TestCase):
    """
    SiteItem
    """

    def setUp(self):
        self.item = SiteItem('/item.html', 'item.html')

    # Url

    def test_url_styles(self):
        """should change url using built-in styles"""

        # pretty-html

        self.item.url = 'pretty-html'
        self.assertEqual('/item/index.html', self.item.url)

        # default

        self.item.url = 'default'
        self.assertEqual('/item.html', self.item.url)

    def test_url_keywords(self):
        """should change url using keywords"""

        # path

        self.item.url = '/:path/foo'
        self.assertEqual('/foo', self.item.url)

        y = SiteItem('/blog/post.md', 'blog/post.md')
        y.url = '/:path/foo'
        self.assertEqual('/blog/foo', y.url)

        # name

        self.item.url = '/:name'
        self.assertEqual('/item', self.item.url)

        # filename

        self.item.url = '/:filename'
        self.assertEqual('/item.html', self.item.url)

        # extension

        self.item.url = '/:extension'
        self.assertEqual('/html', self.item.url)