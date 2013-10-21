from stado.core.content import Content
from tests.plugins import TestPlugin


class TestBefore(TestPlugin):


    def test_without_argument(self):
        """Before plugin should call function without argument."""

        # site.py

        @self.app.before('page.html')
        def test():
            return {'badger': 'badger'}
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('badger', page.read())



    def test_path_argument(self):
        """Before plugin should call function with correct page argument."""

        # site.py

        @self.app.before('page.html')
        def test(page):
            self.assertIsInstance(page, Content)
            return {'badger': page.source}
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('page.html', page.read())


    def test_multiple_path_arguments(self):
        """Before plugin should call function with multiple page arguments."""

        # site.py

        @self.app.before('page.html', 'html.html')
        def test():
            return {'badger': 'test'}
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('test', page.read())
        with open('html.html') as page:
            self.assertEqual('test', page.read())


    def test_filename_matching(self):
        """Before plugin should support filename matching."""

        # site.py

        @self.app.before('*.*')
        def test():
            return {'badger': 'test'}
        self.app.run()

        # tests

        with open('page.html') as page:
            self.assertEqual('test', page.read())
        with open('html.html') as page:
            self.assertEqual('test', page.read())
        with open('markdown.html') as page:
            self.assertEqual('<p>test</p>', page.read())


    def test_overwrite_yaml(self):
        """Before plugin should overwrite context from yaml file."""

        # site.py

        @self.app.before('yaml.yaml')
        def test():
            return {'badger': 'test'}
        self.app.run()

        # tests

        with open('yaml.html') as page:
            self.assertCountEqual('badger: test\none: 1\n', page.read())


    def test_overwrite_json(self):
        """Before plugin should overwrite context from json file."""

        # site.py

        @self.app.before('json.json')
        def test():
            return {'badger': 'test'}
        self.app.run()

        # tests

        with open('json.html') as page:
            self.assertCountEqual('{"badger": "test", "one": 1}', page.read())
