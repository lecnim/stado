import os
from tests.functional import FunctionalTest


class BuildModule(FunctionalTest):
    """User runs command: build <module.py>"""

    cmd = 'build'

    def test_build_module(self):
        """when user build a module file
        then build all site instances in the module"""

        self.prepare_files(
            """
            site.py: |
                from stado import route, Site
                route('/dog.html', 'wow')
                Site().route('/cat.html', 'meow')
            """
        )

        with self.run_console(self.cmd + ' site.py'):
            pass

        self.file_equal('{output}/dog.html', 'wow')
        self.file_equal('{output}/cat.html', 'meow')

    def test_exception(self):
        """when a module raises an exception then exit"""

        self.prepare_files(
            """
            site.py: raise ValueError("Just testing! Don't worry be happy!")
            """
        )

        with self.run_console(self.cmd + ' site.py'):
            pass

    def test_path_not_found(self):
        """when user wants to build a not existing module file then exit"""

        with self.run_console(self.cmd + ' not/exists.py'):
            pass

    def test_custom_source_path(self):
        """when user build site with custom source path
        than build the site using custom source path"""

        self.prepare_files(
            """
            site.py: |
                from stado import Site
                Site('a').build()
                Site('{}').build()
            a/cat.html: meow
            b/dog.html: wow
            """.format(os.path.abspath('b'))
        )

        with self.run_console(self.cmd + ' site.py'):
            pass

        self.same_files('a/cat.html', 'a/{output}/cat.html')
        self.same_files('b/dog.html', 'b/{output}/dog.html')

    def test_custom_output_path(self):
        """when user build site with custom output path
        than build the site in a custom output"""

        self.prepare_files(
            """
            site.py: |
                from stado import Site
                Site(output='a').route('/cat.html', 'meow')
                Site(output='{}').route('/dog.html', 'wow')
            """.format(os.path.abspath('b'))
        )

        with self.run_console(self.cmd + ' site.py'):
            pass

        self.same_files('a/cat.html', 'a/cat.html')
        self.same_files('b/dog.html', 'b/dog.html')


class BuildPackage(FunctionalTest):
    """User runs command: build <package>"""

    cmd = 'build'

    def test_absolute_path_argument(self):
        """when user use absolute path as a command argument
        then build package from absolute path"""

        self.prepare_files(
            """
            x/a.py: |
                from stado import route
                route('/cat.html', 'meow')
            """
        )

        with self.run_console(self.cmd + ' ' + os.path.abspath('x')):
            pass

        self.file_equal('x/{output}/cat.html', 'meow')

    def test_no_command_arguments(self):
        """when user runs build command with no arguments
        then build all sites in current working directory"""

        self.prepare_files(
            """
            a.py: |
                from stado import route
                route('/cat.html', 'meow')
            b.py: |
                from stado import route
                route('/dog.html', 'wow')
            """
        )

        with self.run_console(self.cmd):
            pass

        self.file_equal('{output}/cat.html', 'meow')
        self.file_equal('{output}/dog.html', 'wow')

    def test_build_package(self):
        """when user build a package
        then build all site instances in all modules"""

        self.prepare_files(
            """
            foo/a.py: |
                from stado import route
                route('/cat.html', 'meow')
            foo/b.py: |
                from stado import route
                route('/dog.html', 'wow')
            """
        )

        with self.run_console(self.cmd + ' foo'):
            pass

        self.file_equal('foo/{output}/cat.html', 'meow')
        self.file_equal('foo/{output}/dog.html', 'wow')

    def test_exception_in_module(self):
        """when one of modules raises an exception
        then try to build other modules in the package"""

        self.prepare_files(
            """
            foo/a.py: raise ValueError("Just testing! Don't worry be happy!")
            foo/b.py: |
                from stado import route
                route('/dog.html', 'wow')
            """
        )

        with self.run_console(self.cmd + ' foo'):
            pass

        self.file_equal('foo/{output}/dog.html', 'wow')
