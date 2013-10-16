import os

from stado import config
from commands import UserInterface
from test.test_commands import TestCommand



class TestBuildWithSiteArgument(TestCommand):
    """Tests build command with site argument.

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    def test_build_directory(self):
        """Build command should create build directory in site directory."""

        UserInterface().call('build a')

        # temp/a/_build
        build_directory = os.path.join(self.temp_path, 'a', config.build_dir)
        self.assertTrue(os.path.exists(build_directory))


    def test_page(self):
        """Build command should correctly build page from site content."""

        UserInterface().call('build a')

        # temp/a/_build/a.html
        page_file = os.path.join(self.temp_path, 'a', config.build_dir, 'a.html')

        self.assertTrue(os.path.exists(page_file))
        with open(page_file) as page:
            self.assertEqual('hello world', page.read())


    def test_skip_python_script(self):
        """Build command should skip python files."""

        UserInterface().call('build a')

        # temp/a/_build/site.py
        site_py = os.path.join(self.temp_path, 'a', config.build_dir, 'site.py')

        self.assertFalse(os.path.exists(site_py))



class TestBuildWithoutArguments(TestCommand):
    """Tests build command without arguments.

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    def test_build_directory(self):
        """Build command without arguments should create build directory in each
        site."""

        UserInterface().call('build')

        a = os.path.join(self.temp_path, 'a', config.build_dir)
        b = os.path.join(self.temp_path, 'b', config.build_dir)

        self.assertTrue(os.path.exists(a))
        self.assertTrue(os.path.exists(b))


    def test_page(self):
        """Build command without arguments should correctly build page in each
        site."""

        UserInterface().call('build')

        a = os.path.join(self.temp_path, 'a', config.build_dir, 'a.html')
        b = os.path.join(self.temp_path, 'b', config.build_dir, 'b.html')

        self.assertTrue(os.path.exists(a))
        self.assertTrue(os.path.exists(b))

        with open(a) as page:
            self.assertEqual('hello world', page.read())
        with open(b) as page:
            self.assertEqual('hello world', page.read())


    def test_skip_python_script(self):
        """Build command without arguments should skip python files in each site."""

        UserInterface().call('build')

        a = os.path.join(self.temp_path, 'a', config.build_dir, 'site.py')
        b = os.path.join(self.temp_path, 'b', config.build_dir, 'site.py')

        self.assertFalse(os.path.exists(a))
        self.assertFalse(os.path.exists(b))
