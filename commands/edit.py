import os
import pkgutil

from . import Command
from stado import config as CONFIG


class Edit(Command):

    name = 'edit'

    def install(self, parser):
        parser.add_argument('site')
        parser.add_argument('--output', '-o')
        parser.set_defaults(function=self.run)


    def run(self, site, output=None):
        """Command-line interface will execute this method if user type 'edit'
        command."""

        self.command_line.build(site, output)

        self.command_line.watch(site, output, wait=False)