import os

from stado.core.site import Site
from stado import core
from tests import TestTemporaryDirectory


class TestSite(TestTemporaryDirectory):

    def test_run(self):

        path = os.path.dirname(__file__)

        site = Site(source=os.path.join(path, 'data', 'site'), output=self.temp_path)
        returned = site.run()

        self.assertTrue(returned)

        fp = os.path.join(self.temp_path, 'a.html')
        self.assertTrue(os.path.exists(fp))
        with open(fp) as file:
            self.assertEqual('hello world', file.read())

        self.assertTrue(os.path.exists(os.path.join(self.temp_path, 'a.html')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_path, 'b.jpg')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_path, 'a', 'a.html')))
