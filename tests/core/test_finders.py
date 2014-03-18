from stado.core.finders import FileFinder
from tests import TestInCurrentDirectory


class TestFileFinder(TestInCurrentDirectory):
    """A FileFinder

    This test case change current working directory to __file__ location.
    """

    # Wildcards

    def test_asterisk(self):
        """can use wildcard *"""

        files = [i for i in FileFinder().find('data/*.html')]

        self.assertEqual(2, len(files))
        self.assertCountEqual(['data/index.html', 'data/about.html'], files)

    def test_double_asterisk(self):
        """can use wildcard **"""

        files = [i for i in FileFinder().find('data/**/*.html')]

        self.assertEqual(5, len(files))
        self.assertIn('data/blog/post.html', files)
        self.assertIn('data/blog2/post.html', files)

        # Directories prefix:

        files = [i for i in FileFinder().find('data/b**/*.html')]

        self.assertEqual(2, len(files))
        self.assertCountEqual(['data/blog/post.html',
                               'data/blog2/post.html'],
                              files)

    def test_question(self):
        """can use wildcard: ?"""

        files = [i for i in FileFinder().find('data/?????.html')]

        self.assertEqual(2, len(files))
        self.assertCountEqual(['data/index.html', 'data/about.html'], files)

    # Files and dirs

    def test_file(self):
        """should accept path pointing to file"""

        files = [i for i in FileFinder().find('data/index.html')]
        self.assertIn('data/index.html', files)

    def test_dir(self):
        """should accept path pointing to directory"""

        files = [i for i in FileFinder().find('data/blog2')]
        self.assertEqual(2, len(files))

    # Excluding

    def test_excluded_dirs(self):
        """should correctly exclude directories."""

        files = [i for i in FileFinder().find('data/**',
                                              excluded_paths=['data/blog*'])]
        self.assertEqual(3, len(files))

        files = [i for i in FileFinder().find('data/**',
                                              excluded_paths=['data/blog'])]
        self.assertEqual(5, len(files))


    def test_excluded_files(self):
        """should correctly exclude files"""

        finder = FileFinder()
        files = [i for i in finder.find('data/**',
                                        excluded_paths=['data/index.html'])]

        self.assertEqual(7, len(files))
        self.assertNotIn('data/index.html', files)
