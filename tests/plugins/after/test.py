
import os
from tests import TestTemporaryDirectory
from stado import Stado


class TestAfter(TestTemporaryDirectory):

    def setUp(self):
        TestTemporaryDirectory.setUp(self)

        self.path = os.path.dirname(__file__)
        self.app = Stado(os.path.join(self.path, 'data'))
        self.app.output = self.temp_path


    def test_one_path(self):
        """Before plugin should correctly pass path argument and get context."""

        # site.py

        @self.app.after('a.html')
        def test(path, data):
            return path

        self.app.run()


        # tests

        with open(os.path.join(self.temp_path, 'a.html')) as page:
            self.assertEqual('a.html', page.read())