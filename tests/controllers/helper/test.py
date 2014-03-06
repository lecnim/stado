from tests.controllers import TestPlugin


class TestHelper(TestPlugin):
    """
    Controller @helper
    """


    def test_executing(self):
        """should run function only when template is calling"""

        # site.py

        self.was_executed = False

        @self.app.helper
        def not_executed():
            self.was_executed = True
        self.app.run()

        # tests

        self.assertFalse(self.was_executed)

    def test_layout(self):
        """should be available during rendering layout"""

        # site.py

        @self.app.helper
        def hello():
            return 'hello world'
        self.app.layout('str.html', 'layout.html')
        self.app.run()

        # tests

        with open('str.html') as page:
            self.assertEqual('hello world not', page.read())


    # Test types.

    def test_str(self):
        """should works correctly if string returned"""

        # site.py

        @self.app.helper
        def hello():
            return 'hello world'
        self.app.run()

        # tests

        with open('str.html') as page:
            self.assertEqual('hello world', page.read())


    def test_list(self):
        """should works correctly if list returned"""

        # site.py

        @self.app.helper
        def test():
            return [1, 2, 3]
        self.app.run()

        # tests

        with open('list.html') as page:
            self.assertEqual('1\n2\n3\n', page.read())


    def test_list_of_dict(self):
        """should works correctly if list of dict returned"""

        # site.py

        @self.app.helper
        def test():
            return [{'a': 1}, {'a': 2}, {'a':3}]
        self.app.run()

        # tests

        with open('list_of_dict.html') as page:
            self.assertEqual('1\n2\n3\n', page.read())


    def test_dict(self):
        """should works correctly if dict returned"""

        # site.py

        @self.app.helper
        def test():
            return {'key': 'value'}
        self.app.run()

        # tests

        with open('dict.html') as page:
            self.assertEqual('value', page.read())


    # Other tests.

    def test_do_not_overwrite_context(self):
        """should not overwrite already existing context key"""

        # site.py

        @self.app.before('str.html')
        def page(path):
            return {'hello': 'hello world'}

        @self.app.helper
        def hello():
            return 'test'
        self.app.run()

        # tests

        with open('str.html') as page:
            self.assertEqual('hello world', page.read())
        with open('yaml.yaml') as page:
            self.assertEqual('hello: hello world\n', page.read())
        with open('json.json') as page:
            self.assertEqual('{"hello": "hello world"}', page.read())
