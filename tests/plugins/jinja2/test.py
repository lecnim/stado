import os
from tests.plugins import TestPlugin


class TestJinja2(TestPlugin):
    """
    Plugin Jinja2
    """

    def test_substitution(self):
        """should correctly substitute variables"""

        self.site.build('basic.html', 'jinja2', context={'title': 'hello'})
        self.assertTrue(os.path.exists('basic.html'))
        with open('basic.html') as page:
            self.assertEqual('hello', page.read())

    def test_inheritance(self):
        """should support template inheritance"""

        self.site.build('inheritance/page.html',
                        'jinja2')
        self.assertTrue(os.path.exists('inheritance/page.html'))
        with open('inheritance/page.html') as page:
            self.assertEqual('hello badger', page.read())