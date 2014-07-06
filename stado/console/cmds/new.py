"""New command."""

import os
import textwrap
from . import Command
from ..errors import CommandError
from .. import log


# TODO: Elaborated new site files...

FILES = {

    'site.py':
        """\
        from stado import build
        # Start coding here:
        build('index.html')
        """,

    'index.html':
        """\
        You have just create the new stado site!
        """
}


class New(Command):
    """Creates new site."""

    name = 'new'
    usage = '{cmd} [site_name]'
    summary = 'Create new site.'

    #

    def _parser_add_arguments(self, parser):
        parser.add_argument('site')

    #

    def run(self, site):
        """Command-line interface will execute this method if user type 'new'
        command."""

        if os.path.exists(site):
            raise CommandError('Site already exists!')

        os.makedirs(site, exist_ok=True)

        for file_name, data in FILES.items():
            log.debug('Writing ' + file_name)

            with open(os.path.join(site, file_name), 'w',
                      encoding='utf8') as file:
                file.write(textwrap.dedent(data))

        log.info('New site "{}" successfully created!'.format(site))
        return True