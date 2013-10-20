import os
from tests import TestTemporaryDirectory
from stado import Stado


class TestPermalink(TestTemporaryDirectory):

    def setUp(self):
        TestTemporaryDirectory.setUp(self)

        self.path = os.path.dirname(__file__)
        self.app = Stado(os.path.join(self.path, 'data'))
        self.app.output = self.temp_path


    def test_path(self):

        # site.py

        self.app.permalink('a.html', 'b.html')
        self.app.run()


        # tests

        with open(os.path.join(self.temp_path, 'b.html')) as page:
            self.assertEqual('hello world', page.read())
