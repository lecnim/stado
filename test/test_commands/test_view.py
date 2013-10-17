import os
import urllib.request

from stado import config
from commands import UserInterface
from test.test_commands import TestCommand



class TestViewWithArguments(TestCommand):
    """Tests: view [site] [host] [port]

    Important!
    This test is done in temporary directory. Use self.temp_path to get path to it.
    During tests current working directory is self.temp_path. Previous working
    directory is self.cwd.

    """

    def setUp(self):
        TestCommand.setUp(self)

        self.ui = UserInterface()


    def test_view_site(self):
        """Build command should create build directory in site directory."""

        self.ui.after_build = self._test_view_site
        self.ui.call('view a')

        # temp/a/_build
        build_directory = os.path.join(self.temp_path, 'a', config.build_dir)
        self.assertTrue(os.path.exists(build_directory))

    def _test_view_site(self):
        # Getting content from urls.
        #a = urllib.request.urlopen('http://localhost:8000/hello').read()
        #b = urllib.request.urlopen('http://localhost:8000/empty/a').read()
        self.ui.commands['view'].server.stop()

        #self.assertEqual('hello world', a.decode('UTF-8'))
        #self.assertEqual('hello world', b.decode('UTF-8'))


    #def test_page(self):
    #    """Build command should correctly build page from site content."""
    #
    #    UserInterface().call('build a')
    #
    #    # temp/a/_build
    #    build_directory = os.path.join(self.temp_path, 'a', config.build_dir)
    #
    #    self.assertEqual(['a.html'], os.listdir(build_directory))
    #    with open(os.path.join(build_directory, 'a.html')) as page:
    #        self.assertEqual('hello world', page.read())
    #
    #
    #def test_skip_python_script(self):
    #    """Build command should skip python files."""
    #
    #    UserInterface().call('build a')
    #
    #    # temp/a/_build/site.py
    #    site_py = os.path.join(self.temp_path, 'a', config.build_dir, 'site.py')
    #
    #    self.assertFalse(os.path.exists(site_py))



#class TestBuildWithoutArguments(TestCommand):
#    """Tests: build
#
#    Important!
#    This test is done in temporary directory. Use self.temp_path to get path to it.
#    During tests current working directory is self.temp_path. Previous working
#    directory is self.cwd.
#
#    """
#
#    def test_build_directory(self):
#        """Build command without arguments should create build directory in each
#        site."""
#
#        UserInterface().call('build')
#
#        a = os.path.join(self.temp_path, 'a', config.build_dir)
#        b = os.path.join(self.temp_path, 'b', config.build_dir)
#
#        self.assertTrue(os.path.exists(a))
#        self.assertTrue(os.path.exists(b))
#
#
#    def test_page(self):
#        """Build command without arguments should correctly build page in each
#        site."""
#
#        UserInterface().call('build')
#
#        a = os.path.join(self.temp_path, 'a', config.build_dir, 'a.html')
#        b = os.path.join(self.temp_path, 'b', config.build_dir, 'b.html')
#
#        self.assertTrue(os.path.exists(a))
#        self.assertTrue(os.path.exists(b))
#
#        with open(a) as page:
#            self.assertEqual('hello world', page.read())
#        with open(b) as page:
#            self.assertEqual('hello world', page.read())
#
#
#    def test_skip_python_script(self):
#        """Build command without arguments should skip python files in each site."""
#
#        UserInterface().call('build')
#
#        a = os.path.join(self.temp_path, 'a', config.build_dir, 'site.py')
#        b = os.path.join(self.temp_path, 'b', config.build_dir, 'site.py')
#
#        self.assertFalse(os.path.exists(a))
#        self.assertFalse(os.path.exists(b))
