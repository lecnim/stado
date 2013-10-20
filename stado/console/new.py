"""Command: new"""

import os
from . import Command, CommandError


script = """\
from stado import Stado
app = Stado()

#  Start coding here!

app.run()
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

        with open(os.path.join(site, 'site.py'), 'w', encoding='utf8') as file:
            file.write(script)

        # index.html

        with open(os.path.join(site, 'index.html'), 'w', encoding='utf8') as file:
            file.write(index)

        return True