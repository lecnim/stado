import unittest
from stado.core.item import SiteItem


class TestItem(unittest.TestCase):
    """

    """

    def test_posix_source(self):
        """Item.source property should use posix path format."""

        item = SiteItem('a/b/c', '')
        self.assertEqual('a/b/c', item.source)

        item = SiteItem('a\\b\\c', '')
        self.assertEqual('a/b/c', item.source)
