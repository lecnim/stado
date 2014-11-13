from stado import config
from tests.functional import FunctionalTest


class ViewPackage(FunctionalTest):

    cmd = 'view'

    # Tests:

    def test_no_command_arguments(self):
        """when user runs view command with no arguments
        then view sites from all modules in current working directory"""

        self.prepare_files(
            """
            a.py: |
                from stado import Site
                Site(output='a').route('/dog.html', 'wow')
            b.py: |
                from stado import Site
                Site(output='b').route('/cat.html', 'meow')
            """
        )

        with self.run_console(self.cmd):
            self.url_equal(
                'http://{}:{}/dog.html'.format(config.host, config.port),
                'wow')
            self.url_equal(
                'http://{}:{}/cat.html'.format(config.host, config.port + 1),
                'meow')

    def test_serve_custom_output_files(self):
        """when user views a site from package
        then correct output files should be served"""

        self.prepare_files(
            """
            foo/a.py: |
                from stado import route, Site
                Site(output='custom/build').route('/dog.html', 'wow')
            """
        )

        with self.run_console(self.cmd + ' foo'):
            self.url_equal(
                'http://{}:{}/dog.html'.format(config.host, config.port),
                'wow')

    def test_port_order(self):
        """when user views a package
        then site instances from each module should have correct port"""

        # In alphabetical order of script file name, for example:
        # a.py => 4000
        # b.py => 4001
        # c.py => 4002

        self.prepare_files(
            """
            foo/a.py: |
                from stado import route
                route('/cat.html', 'meow')
            foo/b.py: |
                from stado import route
                route('/dog.html', 'wow')
            foo/c.py: |
                from stado import route
                route('/mouse.html', 'pii')
            """
        )

        with self.run_console(self.cmd + ' foo'):
            self.url_equal(
                'http://{}:{}/cat.html'.format(config.host, config.port),
                'meow')
            self.url_equal(
                'http://{}:{}/dog.html'.format(config.host, config.port + 1),
                'wow')
            self.url_equal(
                'http://{}:{}/mouse.html'.format(config.host, config.port + 2),
                'pii')


class ViewModule(FunctionalTest):

    cmd = 'view'

    # Tests:

    def test_serve_custom_output_files(self):
        """when user views a site url
        then correct output files should be served"""

        self.prepare_files(
            """
            site.py: |
                from stado import route, Site
                route('/cat.html', 'meow')
                Site(output='build').route('/dog.html', 'wow')
            """
        )

        with self.run_console(self.cmd + ' site.py'):
            self.url_equal(
                'http://{}:{}/cat.html'.format(config.host, config.port),
                'meow')
            self.url_equal(
                'http://{}:{}/dog.html'.format(config.host, config.port + 1),
                'wow')

    def test_custom_host_and_port(self):
        """when user runs a command with custom host and port arguments
        then serve output files on a correct host and port"""

        self.prepare_files(
            """
            site.py: |
                from stado import route, Site
                route('/cat.html', 'meow')
            """
        )

        with self.run_console(self.cmd + ' site.py -s 127.0.0.2 -p 3000'):
            self.url_equal('http://127.0.0.2:3000/cat.html', 'meow')

    def test_port_order(self):
        """when user views multiple site instances
        then each site instance should have correct port number"""

        self.prepare_files(
            """
            site.py: |
                from stado import Site
                Site(output='a').route('/cat.html', 'meow')
                Site(output='b').route('/dog.html', 'wow')
                Site(output='c').route('/mouse.html', 'pii')
            """
        )

        with self.run_console(self.cmd + ' site.py'):
            self.url_equal(
                'http://{}:{}/cat.html'.format(config.host, config.port),
                'meow')
            self.url_equal(
                'http://{}:{}/dog.html'.format(config.host, config.port + 1),
                'wow')
            self.url_equal(
                'http://{}:{}/mouse.html'.format(config.host, config.port + 2),
                'pii')

    def test_path_not_found(self):
        """when a module file not found then exit"""

        with self.run_console(self.cmd + ' not/exists.py'):
            pass

    def test_site_exception(self):
        """when one of site instances throw an exception
        then try to view other site instances"""

        self.prepare_files(
            """
            site.py: |
                from stado import route
                route('/cat.html', 'meow')
                raise ValueError("Just testing! Don't worry be happy!")
            """)

        with self.run_console(self.cmd + ' site.py'):
            self.url_equal(
                'http://{}:{}/cat.html'.format(config.host, config.port),
                'meow')

    def test_module_exception(self):
        """when module throw an exception and there are no site instances
        then exit"""

        self.prepare_files(
            """
            site.py: |
                from stado import route
                raise ValueError("Just testing! Don't worry be happy!")
            """)

        with self.run_console(self.cmd + ' site.py'):
            pass

    def test_empty_module(self):
        """when user views a module without any site instance then exit"""

        self.prepare_files("site.py: '\n'")
        with self.run_console(self.cmd + ' site.py'):
            pass