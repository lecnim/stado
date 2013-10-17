import os
import pkgutil
import time

from . import Command
from stado import config as CONFIG


class Edit(Command):

    name = 'edit'

    def __init__(self, command_line):
        Command.__init__(self, command_line)

        self.stopped = True

    def install(self, parser):
        parser.add_argument('site')
        parser.add_argument('--port', '-p', type=int, default=4000)
        parser.add_argument('--host', '-h', default='localhost')
        parser.add_argument('--output', '-o')
        parser.set_defaults(function=self.run)


    def run(self, site, host, port, output=None):
        """Command-line interface will execute this method if user type 'edit'
        command."""

        self.event('before_edit')

        self.stopped = False

        #self.command_line.build(site, output)
        #self.command_line.watch(site, output, wait=False)
        print(host, port)
        self.command_line.view(site, host, port, output, wait=False)

        # Monitoring.
        self.event('before_waiting')

        while not self.stopped:
            time.sleep(.2)

        self.event('after_edit')

    def stop(self):
        self.stopped = True