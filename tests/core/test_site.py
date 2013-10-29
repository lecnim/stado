import os

from stado.core.site import Site
from tests import TestTemporaryDirectory


class TestSite(TestTemporaryDirectory):

    def test_run(self):

        path = os.path.dirname(__file__)

        site = Site(path=os.path.join(path, 'data'), output=self.temp_path)
        site.run()

        fp = os.path.join(self.temp_path, 'a.html')
        self.assertTrue(os.path.exists(fp))
        with open(fp) as file:
            self.assertEqual('a', file.read())

        self.assertTrue(os.path.exists(os.path.join(self.temp_path, 'a.html')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_path, 'image.jpg')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_path, 'b', 'b.html')))
