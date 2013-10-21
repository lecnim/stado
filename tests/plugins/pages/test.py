import os
from tests.plugins import TestPlugin


class TestPages(TestPlugin):

    def test(self):
        """Pages plugin should correctly yields pages from path."""

        # site.py

        @self.app.helper
        def pages():

            i = sorted([i for i in self.app.pages('*.*')], key=lambda x: x.source)
            for k in i:
                print(k.source)
        self.app.run()

        # tests

        with open('page.html') as file:
            a = os.path.join('a', 'page.html')
            self.assertEqual(a + "\nmarkdown.md\npage.html\n", file.read())
