import textwrap
from stado.console.cmds.new import FILES
from tests.functional import FunctionalTest


class New(FunctionalTest):
    """User runs command: new <path>"""

    cmd = 'new'

    # Tests:

    def test(self):
        """when user creates new site then create correct site source files"""

        with self.run_console(self.cmd + ' test'):
            pass

        for file_name, data in FILES.items():
            self.file_equal('test/' + file_name, textwrap.dedent(data))

    def test_site_exists(self):
        """when user want to create already existing site then exit"""

        self.new_file('example/dog.html')

        with self.run_console(self.cmd + ' example'):
            pass

        self.count_files('example', 1)