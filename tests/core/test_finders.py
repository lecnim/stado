from stado.core.finders import FileFinder
from tests import TestStado


class TestFileFinder(TestStado):
    """A FileFinder

    This test case change current working directory to __file__ location.
    """

    # Wildcards

    def test_asterisk(self):
        """can use wildcard *"""

        self.create_file('data/a.html')
        self.create_file('data/b.html')
        self.create_file('data/foo/bar.html')

        files = [i for i in FileFinder().find('data/*.html')]

        self.assertEqual(2, len(files))
        self.assertCountEqual(['data/a.html', 'data/b.html'], files)

    def test_double_asterisk(self):
        """can use wildcard **"""

        self.create_file('data/a.html')
        self.create_file('data/b.html')
        self.create_file('data/foo/bar.html')
        self.create_file('data/foo2/bar.html')

        files = [i for i in FileFinder().find('data/**/*.html')]

        self.assertEqual(4, len(files))
        self.assertIn('data/a.html', files)
        self.assertIn('data/b.html', files)
        self.assertIn('data/foo/bar.html', files)
        self.assertIn('data/foo2/bar.html', files)

        # Directories prefix:

        files = [i for i in FileFinder().find('data/f**/*.html')]

        self.assertEqual(2, len(files))
        self.assertCountEqual(['data/foo/bar.html', 'data/foo2/bar.html'],
                              files)

    def test_question(self):
        """can use wildcard: ?"""

        self.create_file('data/a.html')
        self.create_file('data/b.html')
        self.create_file('data/ab.html')

        files = [i for i in FileFinder().find('data/?.html')]

        self.assertEqual(2, len(files))
        self.assertCountEqual(['data/a.html', 'data/b.html'], files)

    # Files and dirs

    def test_file(self):
        """should accept path pointing to file"""

        self.create_file('data/index.html')

        files = [i for i in FileFinder().find('data/index.html')]
        self.assertIn('data/index.html', files)

    def test_dir(self):
        """should accept path pointing to directory"""

        self.create_file('data/a.html')
        self.create_file('data/b.html')

        files = [i for i in FileFinder().find('data')]
        self.assertEqual(2, len(files))
        self.assertCountEqual(['data/a.html', 'data/b.html'], files)

    # Excluding

    def test_excluded_dirs(self):
        """should correctly exclude directories."""

        self.create_file('data/a.html')
        self.create_file('data/foo/a.html')
        self.create_file('data/foobar/a.html')
        self.create_file('data/foo/bar/a.html')

        files = [i for i in FileFinder().find('data/**',
                                              excluded_paths=['data/foo*'])]
        self.assertEqual(1, len(files))

        files = [i for i in FileFinder().find('data/**',
                                              excluded_paths=['data/foo'])]
        self.assertEqual(2, len(files))

    def test_excluded_files(self):
        """should correctly exclude files"""

        self.create_file('data/a.html')
        self.create_file('data/foo/a.html')

        finder = FileFinder()
        files = [i for i in finder.find('data/**',
                                        excluded_paths=['data/a.html'])]

        self.assertEqual(1, len(files))
        self.assertNotIn('data/a.html', files)