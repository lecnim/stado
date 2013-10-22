import os
from tests.examples import TestExample


class TestBasicSite(TestExample):

    def test(self):

        self.console('build basic --output ' + self.temp_path)

        # Check pages.

        with open(os.path.join(self.temp_path, 'index.html')) as page:
            self.assertEqual('Basic site\nHello on index!', page.read())

        with open(os.path.join(self.temp_path, 'contact.html')) as page:
            self.assertEqual('Basic site\nexample@site.com', page.read())

        with open(os.path.join(self.temp_path, 'about.html')) as page:
            self.assertEqual('<p>Basic site\nAbout...</p>', page.read())

        i = os.path.exists(os.path.join(self.temp_path, 'ignored.html'))
        self.assertFalse(i)
