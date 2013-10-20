
import os
from tests import TestTemporaryDirectory
from stado import Stado


class TestBefore(TestTemporaryDirectory):

    def setUp(self):
        TestTemporaryDirectory.setUp(self)

        self.path = os.path.dirname(__file__)
        self.app = Stado(os.path.join(self.path, 'data'))
        self.app.output = self.temp_path


    def test_one_path(self):
        """Before plugin should correctly pass path argument and get context."""

        # site.py

        @self.app.before('a.html')
        def test(path):
            return {'hello': path}

        self.app.run()


        # tests

        with open(os.path.join(self.temp_path, 'a.html')) as page:
            self.assertEqual('a.html', page.read())



    def test_multiple_paths(self):
        """Before plugin should add context to multiple contents."""

        # site.py

        @self.app.before('a.html', 'b.html')
        def test(path):
            return {'hello': 'hello before'}

        self.app.run()


        # tests

        with open(os.path.join(self.temp_path, 'a.html')) as page:
            self.assertEqual('hello before', page.read())
        with open(os.path.join(self.temp_path, 'b.html')) as page:
            self.assertEqual('hello before', page.read())



    def test_overwrite(self):
        """Before plugin should overwrite yaml or json file context."""

        # site.py

        @self.app.before('c.yaml')
        def test(path):
            return {'hello': 'hello before'}

        self.app.run()


        # tests

        with open(os.path.join(self.temp_path, 'c.html')) as page:
            print(page.read())