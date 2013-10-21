import os
from tests.plugins import TestPlugin


class TestPages(TestPlugin):

    def test(self):
        """Pages plugin should correctly yields pages from path."""

        # site.py

        @self.app.helper
        def pages():

            print([i for i in self.app.cache.keys()])
            print('...')
            print(self.app.site.cache.files)
            print('...')

            i = sorted([i for i in self.app.pages('*.*')], key=lambda x: x.source)
            for k in i:
                print(k.source)
            return i
        self.app.run()

        # tests

        with open('page.html') as file:
            a = os.path.join('a', 'page.html')
            self.assertEqual(a + "\nmarkdown.md\npage.html\n", file.read())
