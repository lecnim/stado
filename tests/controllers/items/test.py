from tests.controllers import TestPlugin


class TestFind(TestPlugin):
    """Find controller"""

    def test_greedy_matching(self):
        """should use file matching: **"""

        pages = [i.permalink for i in self.app.find('**.html')]
        self.assertCountEqual(['/index.html', '/about/index.html'], pages)

    def test_dir_matching(self):
        """should use file matching: *"""

        pages = [i.permalink for i in self.app.find('*.html')]
        self.assertEqual(['/index.html'], pages)


class TestGet(TestPlugin):
    """Get controller"""

    def test(self):
        """should return correct item"""

        page = self.site.get('index.html')
        self.assertEqual('/index.html', page.permalink)