from tests.functional import FunctionalTest


# TODO: Add Watch package
# TODO: Add watch without argument

class Watch(FunctionalTest):

    cmd = 'watch'

class WatchPackage(FunctionalTest):
    """User runs command: watch <package>"""

    cmd = 'watch'

    # Tests.

    # TODO: Absolute path to package.

    def test_modify_site_source(self):
        """when user modifies a site source file then rebuild this site"""

        self.prepare_files(
            """
            foo/a.py: |
                from stado import Site
                Site('a').build()
            foo/a/cat.txt: hello
            foo/b.py: |
                from stado import Site
                Site('b').build()
            foo/b/dog.txt: hello
            """)

        with self.run_console(self.cmd + ' foo'):
            self.modify_file('foo/a/cat.txt', 'meow')
            self.modify_file('foo/b/dog.txt', 'wow')
            self.wait_until_file_equal('foo/b/{output}/dog.txt', 'wow')
            self.modify_file('foo/b/dog.txt', 'meow')

        # Test:
        self.count_files('foo/a/{output}', 1)
        self.count_files('foo/b/{output}', 1)
        self.same_files('foo/a/cat.txt', 'foo/a/{output}/cat.txt')
        self.same_files('foo/b/dog.txt', 'foo/b/{output}/dog.txt')

    def test_new_source_file(self):
        """when user creates a new file in a site source directory
        then rebuild this site"""

        self.prepare_files(
            """
            foo/site.py: |
                from stado import Site
                Site('a').build()
            foo/a/page.txt: hello
            """)

        with self.run_console(self.cmd + ' foo'):
            self.new_file('foo/a/dog.html', 'wow')
            self.wait_until_file_equal('foo/a/{output}/dog.html', 'wow')
            self.new_file('foo/a/cat.html', 'meow')

        # Test:
        self.count_files('foo/a/{output}', 3)
        self.same_files('foo/a/page.txt', 'foo/a/{output}/page.txt')
        self.same_files('foo/a/cat.html', 'foo/a/{output}/cat.html')

    def test_delete_source_file(self):
        """when user deletes a file from a site source then rebuild this site"""

        self.prepare_files(
            """
            foo/site.py: |
                from stado import build, remove_output
                remove_output()
                build()
            foo/a.txt: hello
            foo/b.txt: world
            """)

        with self.run_console(self.cmd + ' foo'):
            self.remove_file('foo/a.txt')

        # Test:
        self.count_files('foo/{output}', 1)
        self.same_files('foo/b.txt', 'foo/{output}/b.txt')

    def test_new_module_file(self):
        """when user creates a new module file in a watched package
        then build site instances from this module"""

        self.prepare_files(
            """
            foo/a.py: |
                from stado import route
                route('/a.html', 'hello')
            """)

        with self.run_console(self.cmd + ' foo'):
            self.new_file('foo/b.py',

                          'from stado import route\n'
                          'route("/b.html", "world")')

        # Test:
        self.count_files('foo/{output}', 2)
        self.file_equal('foo/{output}/a.html', 'hello')
        self.file_equal('foo/{output}/b.html', 'world')

    def test_delete_module_file(self):
        """when user deletes a module file from a watched package
        then do not watch site instances from this module"""

        self.prepare_files(
            """
            foo/a.py: |
                from stado import Site
                Site('a').build()
            """)

        with self.run_console(self.cmd + ' foo'):
            self.remove_file('foo/a.py')
            self.new_file('foo/a/new.file')

        # Test:
        self.count_files('foo/a/{output}', 0)

    def test_modify_module_file(self):
        """when user modifies a site module file from a watched package
        then rebuild the site including changes in the module"""

        self.prepare_files(
            """
            foo/a.py: |
                from stado import route
                route('/a.txt', 'yes')
            """)

        with self.run_console(self.cmd + ' foo'):
            self.modify_file('foo/a.py',

                             'from stado import route\n'
                             'route("/a.txt", "no")')

        # Test:
        self.count_files('foo/{output}', 1)
        self.file_equal('foo/{output}/a.txt', 'no')


    def test_new_site_instance_in_module_file(self):
        """when user adds a new site instance to the site module from a watched package
        then rebuild all site instances in module file including new ones"""

        self.prepare_files(
            """
            foo/a.py: |
                from stado import route
                route("/a.txt", "a")
            """)

        with self.run_console(self.cmd + ' foo'):
            self.modify_file('foo/a.py',

                             'from stado import route, Site\n'
                             'route("/a.txt", "a")\n'
                             'Site().route("/b.txt","b")')

        # Tests:
        self.count_files('foo/{output}', 2)
        self.file_equal('foo/{output}/a.txt', 'a')
        self.file_equal('foo/{output}/b.txt', 'b')

    def test_exception_in_module_file(self):
        """when a module from a watched package raises an exception
        then wait until an error is fixed"""

        self.prepare_files(
            """
            foo/a.py: raise ValueError("do not worry - just test")
            """)

        with self.run_console(self.cmd + ' foo'):
            self.modify_file('foo/a.py',

                             'from stado import Site\n'
                             'Site("a").route("/page.txt", "world")')

        self.file_equal('foo/a/{output}/page.txt', 'world')

    def test_exception_do_not_stops_build(self):
        """when a one module raises an exception
        then try to build site instances from other modules"""

        self.prepare_files(
            """
            foo/a.py: raise ValueError("do not worry - just test")
            foo/b.py: |
                from stado import Site
                Site('b').route('/page.txt', 'hello')
            """)

        with self.run_console(self.cmd + ' foo'):
            self.file_equal('foo/b/{output}/page.txt', 'hello')

    def test_directory_not_found(self):
        """when user wants to watch a not existing package then exit"""

        with self.run_console(self.cmd + ' missing/directory'):
            pass

    def test_empty_directory(self):
        """when user wants to watch an empty package then wait for changes"""

        self.create_dir('foo')

        with self.run_console(self.cmd + ' foo'):
            self.new_file('foo/site.py',

                          'from stado import route\n'
                          'route("/a.txt", "a")')

        self.file_equal('foo/{output}/a.txt', 'a')

class WatchModule(FunctionalTest):
    """User runs command: watch <module.py>"""

    cmd = 'watch'

    # Tests.

    # TODO: Test absolute path to module.py

    def test_custom_source(self):
        """when user modifies a file in a custom source directory
        then rebuild the site"""

        self.prepare_files(
            """
            site.py: |
               from stado import Site
               Site(path='x').build()
            x/a.txt: foo
            """)

        with self.run_console(self.cmd + ' site.py'):
            self.modify_file('x/a.txt', 'bar')

        # Test:
        self.same_files('x/a.txt', 'x/{output}/a.txt')

    def test_modify_site_source(self):
        """when user modifies a site source file then rebuild the site"""

        self.prepare_files(
            """
            site.py: |
                from stado import build
                build()
            a.txt: hello
            """)

        with self.run_console(self.cmd + ' site.py'):
            self.modify_file('a.txt', 'world')
            self.wait_until_file_equal('{output}/a.txt', 'world')
            self.modify_file('a.txt', 'badger')

        # Test:
        self.count_files('{output}', 1)
        self.same_files('a.txt', '{output}/a.txt')

    def test_new_source_file(self):
        """when user creates a new file in a site source directory
        then rebuild the site"""

        self.prepare_files(
            """
            site.py: |
                from stado import build
                build()
            """)

        with self.run_console(self.cmd + ' site.py'):
            self.new_file('new.file', 'foo')
            self.wait_until_file_equal('{output}/new.file', 'foo')
            self.new_file('hello.txt', 'world')

        # Test:
        self.count_files('{output}', 2)
        self.same_files('new.file', '{output}/new.file')

    def test_delete_source_file(self):
        """when user deletes a file from a site source then rebuild the site"""

        self.prepare_files(
            """
            site.py: |
                from stado import build, remove_output
                remove_output()
                build()
            a.txt: hello
            b.txt: world
            """)

        with self.run_console(self.cmd + ' site.py'):
            self.remove_file('a.txt')

        # Test:
        self.count_files('{output}', 1)
        self.same_files('b.txt', '{output}/b.txt')

    def test_modify_module_file(self):
        """when user modifies a site module file
        then rebuild the site including changes in the module"""

        self.prepare_files(
            """
            site.py: |
                from stado import build
                build("a.txt")
            a.txt: a
            """)

        with self.run_console(self.cmd + ' site.py'):
            self.modify_file('site.py',

                             'from stado import route\n'
                             'route("/b.txt", "b")')

        # Test:
        self.count_files('{output}', 2)
        self.same_files('a.txt', '{output}/a.txt')
        self.file_equal('{output}/b.txt', 'b')

    def test_new_site_instance_in_module_file(self):
        """when user adds a new site instance to a site module file
        then rebuild all site instances in a module file including new ones"""

        self.prepare_files(
            """
            site.py: |
                from stado import route
                route("/a.txt", "a")
            """)

        with self.run_console(self.cmd + ' site.py'):
            self.modify_file('site.py',

                             'from stado import route, Site\n'
                             'route("/a.txt", "a")\n'
                             'Site().route("/b.txt","b")')

        # Tests:
        self.count_files('{output}', 2)
        self.file_equal('{output}/a.txt', 'a')
        self.file_equal('{output}/b.txt', 'b')

    def test_exception_in_module_file(self):
        """when a module file raises an exception
        then wait until an error is fixed"""

        self.prepare_files(
            """
            site.py: raise ValueError("do not worry - just test")
            """)

        with self.run_console(self.cmd + ' site.py'):
            self.modify_file('site.py',

                             'from stado import route\n'
                             'route("/a.txt", "a")')

        self.file_equal('{output}/a.txt', 'a')

    def test_module_file_not_found(self):
        """when user wants to watch a not existing module file then exit"""

        with self.run_console(self.cmd + ' missing_file.py'):
            pass

    def test_empty_module_file(self):
        """when user wants to watch an empty module file
        then wait for changes"""

        self.prepare_files("site.py: '\n'")

        with self.run_console(self.cmd + ' site.py'):
            self.modify_file('site.py',

                             'from stado import route\n'
                             'route("/a.txt", "a")')

        self.file_equal('{output}/a.txt', 'a')