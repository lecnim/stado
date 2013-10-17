"""Command: edit"""

import os
import time

from . import Command
from stado import config


class Edit(Command):
    """Builds site, watches for changes and runs development server."""

    name = 'edit'

    def __init__(self, command_line):
        Command.__init__(self, command_line)

        self.stopped = True
        self.cwd = None


    def install(self, parser):
        """Add arguments to command line parser."""

        parser.add_argument('site')
        parser.add_argument('--port', '-p', type=int, default=4000)
        parser.add_argument('--host', '-h', default='localhost')
        parser.add_argument('--output', '-o')
        parser.set_defaults(function=self.run)


    def run(self, site, host, port, output=None):
        """Command-line interface will execute this method if user type 'edit'
        command."""

        self.cwd = os.getcwd()
        self.stopped = False

        # Use custom update method.
        self.command_line.commands['watch'].update = self.update
        self.command_line.watch(site, output, wait=False)
        self.command_line.view(site, host, port, output, wait=False)

        # Monitoring.
        self.event('before_waiting')

        while not self.stopped:
            time.sleep(config.wait_interval)



    def update(self, site, output):
        """Overwrites update method in watch command."""

        # TODO: Stop server here.
        #self.command_line.commands['view'].server.stop()

        # Change to previous working directory.
        cwd = os.getcwd()
        os.chdir(self.cwd)
        self.command_line.build(site, output)
        # Change to working directory to site output => server will serve from it.
        os.chdir(cwd)

        # TODO: Start server here.
        #self.command_line.commands['view'].server.restart()

        self.event('after_rebuild')


    def stop(self):
        """Stops command (stops development server and watcher)."""

        self.stopped = True
        