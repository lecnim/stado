"""Command: new"""

import os
from . import Command, CommandError
from .. import log


script = """\
from stado import run

#  Start coding here!

run()
"""

index = """\
You have just created a new stado site!
"""


class New(Command):
    """Creates new site."""

    name = 'new'

    usage = 'new [site_name]'
    summary = 'Create new site.'
    description = ''
    options = []



    def install(self, parser):
        """Add arguments to command line parser."""

        parser.add_argument('site')
        parser.set_defaults(function=self.run)


    def run(self, site):
        """Command-line interface will execute this method if user type 'new'
        command."""

        if os.path.exists(site):
            raise CommandError('Site already exists!')

        os.makedirs(site, exist_ok=True)

        # site.py

        log.debug('Writing site.py')

        with open(os.path.join(site, 'site.py'), 'w', encoding='utf8') as file:
            file.write(script)

        # index.html

        log.debug('Writing index.html')

        with open(os.path.join(site, 'index.html'), 'w', encoding='utf8') as file:
            file.write(index)

        log.info('New site "{}" successfully created!'.format(site))
        return True