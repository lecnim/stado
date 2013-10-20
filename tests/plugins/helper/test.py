
import os
from tests import TestTemporaryDirectory
from stado import Stado


class TestHelper(TestTemporaryDirectory):

    def setUp(self):
        TestTemporaryDirectory.setUp(self)

        self.path = os.path.dirname(__file__)
        self.app = Stado(os.path.join(self.path, 'data'))
        self.app.output = self.temp_path


    def test_one_path(self):
        """Before plugin should correctly pass path argument and get context."""

        # site.py

        @self.app.helper
        def hello():
            return 'hello world'

        self.app.run()


        # tests

        with open(os.path.join(self.temp_path, 'a.html')) as page:
            self.assertEqual('hello world', page.read())
