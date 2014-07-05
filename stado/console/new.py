"""New command."""

import os
from . import Command, CommandError
from .. import log


SCRIPT = """\
from stado import build

# Start coding here:

build('index.html')
"""

INDEX = """\
You have just create the new stado site!
"""


class New(Command):
    """Creates new site."""

    name = 'new'
    usage = '{cmd} [site_name]'
    summary = 'Create new site.'



    # def install_in_parser(self, parser):
    #     """Add arguments to command line parser."""
    #
    #     sub_parser = parser.add_parser(self.name, add_help=False)
    #     sub_parser.add_argument('site')
    #     sub_parser.set_defaults(function=self.run)
    #
    #     return sub_parser

    def _parser_add_arguments(self, parser):
        parser.add_argument('site')


    def run(self, site):
        """Command-line interface will execute this method if user type 'new'
        command."""

        if os.path.exists(site):
            raise CommandError('Site already exists!')

        os.makedirs(site, exist_ok=True)

        # site.py

        log.debug('Writing site.py')

        with open(os.path.join(site, 'site.py'), 'w', encoding='utf8') as file:
            file.write(SCRIPT)

        # index.html

        log.debug('Writing index.html')

        with open(os.path.join(site, 'index.html'), 'w', encoding='utf8') as file:
            file.write(INDEX)

        log.info('New site "{}" successfully created!'.format(site))
        return True