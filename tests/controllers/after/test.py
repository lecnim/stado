from stado.core.content import SiteItem
from tests.controllers import TestPlugin


class TestAfter(TestPlugin):


    def test_no_arguments(self):
        """Controller after should call function without arguments."""

        # site.py

        @self.app.after('page.html')
        def test():
            return 'test'
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('test', page.read())


    def test_page_argument(self):
        """Controller after should call function with page and data arguments."""

        # site.py

        @self.app.after('page.html')
        def test(page, data):
            self.assertIsInstance(page, SiteItem)
            return page.id
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('page.html', page.read())


    def test_data_argument(self):
        """Controller after should call function with correct data argument."""

        # site.py

        @self.app.after('page.html')
        def test(data):
            return data
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('badger', page.read())


    def test_filename_matching(self):
        """Controller after should supports file matching."""

        # site.py

        @self.app.after('*.*')
        def test(path, data):
            return 'test'
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('test', page.read())
        with open('yaml.yaml') as page:
            self.assertEqual('test', page.read())
        with open('json.json') as page:
            self.assertEqual('test', page.read())
        with open('markdown.html') as page:
            self.assertEqual('test', page.read())
