import os
from stado.plugins.layout import Layout

from tests.plugins import TestPlugin

class TestLayout(TestPlugin):
    """
    Plugin layout
    """

    def test_detect_template(self):
        """should auto-detect template engine using file extension"""

        self.site.build('page.html', Layout('layout.mustache'))
        self.assertTrue(os.path.exists('page.html'))
        with open('page.html') as page:
            self.assertEqual('hello world', page.read())

    def test_engine_attribute(self):
        """should use custom engine attribute"""

        self.site.build('page.html', Layout('layout.html', engine='mustache'))
        self.assertTrue(os.path.exists('page.html'))
        with open('page.html') as page:
            self.assertEqual('hello world', page.read())

    def test_context_attribute(self):
        """should use custom context attribute"""

        self.site.build('page.html', Layout('layout_context.mustache',
                                            context={'msg': 'hello'}))
        self.assertTrue(os.path.exists('page.html'))
        with open('page.html') as page:
            self.assertEqual('hello world', page.read())

    def test_item_context(self):
        """has access to item context in template"""

        item = self.site.load('page.html')
        item.context['msg'] = 'hello'

        self.site.build(item, Layout('page_context.mustache'))
        self.assertTrue(os.path.exists('page.html'))
        with open('page.html') as page:
            self.assertEqual('hello world', page.read())

