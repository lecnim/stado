from tests.controllers import TestPlugin


class TestContextController(TestPlugin):
    """A context controller:"""

    # context argument

    def test_dict(self):
        """can get variables from a dict"""

        self.site.context('page.html', {'badger': 'dictionary'})
        self.site.generate()
        with open('page.html') as page:
            self.assertEqual('dictionary', page.read())

    def test_keywords(self):
        """can get variables from keyword arguments (**kwargs)"""

        self.site.context('page.html', badger='keywords')
        self.site.generate()
        with open('page.html') as page:
            self.assertEqual('keywords', page.read())

    def test_function(self):
        """can get variables from calling a function object"""

        def hello(page):
            return {'badger': page.permalink}

        self.site.context('page.html', hello)
        self.site.generate()

        with open('page.html') as page:
            self.assertEqual('/page.html', page.read())

    def test_empty_dict(self):
        """should works even if empty dict is an argument"""

        self.app.context('page.html', {})
        self.app.generate()
        with open('page.html') as page:
            self.assertEqual('', page.read())


    # id argument

    def test_filename_matching(self):
        """should support filename matching"""

        self.app.context('*.*', {'badger': 'test'})
        self.app.generate()

        with open('page.html') as page:
            self.assertEqual('test', page.read())
        with open('html.html') as page:
            self.assertEqual('test', page.read())
        with open('markdown.html') as page:
            self.assertEqual('<p>test</p>', page.read())

    def test_multiple_path_arguments(self):
        """should support multiple id arguments."""

        self.app.context(['page.html', 'html.html'], {'badger': 'test'})
        self.app.generate()

        with open('page.html') as page:
            self.assertEqual('test', page.read())
        with open('html.html') as page:
            self.assertEqual('test', page.read())


    # overwriting context

    def test_overwrite_yaml(self):
        """should overwrite context from loaded yaml file."""

        self.app.context('yaml.yaml', {'badger': 'test'})
        self.app.generate()
        with open('yaml.yaml') as page:
            self.assertEqual('badger: test\none: 1\n', page.read())

    def test_overwrite_json(self):
        """should overwrite context from loaded json file."""

        self.app.context('json.json', {'badger': 'test'})
        self.app.generate()
        with open('json.json') as page:
            self.assertCountEqual('{"badger": "test", "one": 1}', page.read())