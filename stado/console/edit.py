"""Command: edit"""

import os
import time

from . import Command
from .view import View
from .. import config


class Edit(Command):
    """Builds site, watches for changes and runs development server."""

    name = 'edit'

    usage = 'edit [site] [options]'
    summary = 'Build the site, watch for changes and run development server.'
    description = ''
    options = View.options

    def __init__(self, console):
        Command.__init__(self, console)

        self.stopped = True
        self.cwd = None


    def install(self, parser):
        """Add arguments to command line parser."""

        parser.add_argument('site')
        parser.add_argument('--port', '-p', type=int, default=config.port)
        parser.add_argument('--host', '-h', default=config.host)
        parser.add_argument('--output', '-o')
        parser.set_defaults(function=self.run)


    def run(self, site, host, port, output=None):
        """Command-line interface will execute this method if user type 'edit'
        command."""

        self.cwd = os.getcwd()
        self.stopped = False

        # Use custom update method.
        self.console.commands['watch'].update = self.update
        self.console.watch(site, output, wait=False)
        self.console.view(site, host, port, output, wait=False)

        # Monitoring.
        self.event('before_waiting')

        while not self.stopped:
            time.sleep(config.wait_interval)



    def update(self, site, output):
        """Overwrites update method in watch command."""

        # TODO: Stop server here.
        #self.console.commands['view'].server.stop()

        # Change to previous working directory.
        cwd = os.getcwd()
        os.chdir(self.cwd)
        self.console.build(site, output)
        # Change to working directory to site output => server will serve from it.
        os.chdir(cwd)

        # TODO: Start server here.
        #self.console.commands['view'].server.restart()

        self.event('after_rebuild')


    def stop(self):
        """Stops command (stops development server and watcher)."""

        self.stopped = True
        