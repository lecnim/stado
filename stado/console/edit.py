"""Command: edit"""

import os
import time
import threading

from . import Command
from .view import View
from .. import config, Site


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

        parser.add_argument('site', default=None, nargs='?')
        parser.add_argument('--port', '-p', type=int, default=config.port)
        parser.add_argument('--host', '-h', default=config.host)
        parser.add_argument('--output', '-o')
        parser.set_defaults(function=self.run)


    def run(self, site=None, host=None, port=None, output=None):
        """Command-line interface will execute this method if user type 'edit'
        command."""

        for i in threading.enumerate():
            print(i)
            print(i.is_alive())

        while len(threading.enumerate()) > 1:
            pass

        self.cwd = os.getcwd()
        self.stopped = False

        # self.console.build(site, output)
        # Use custom update method.

        # build()
        # get list of build sites
        Site._tracker.enable()
        self.console.build(site, output)

        records = Site._tracker.dump(skip_unused=True)

        # add this sites to watcher
        self.console.commands['watch'].file_monitor.stop()
        self.console.commands['watch'].file_monitor.clear()
        self.console.commands['watch'].event_update = self.update

        outputs = [i['output'] for i in records if i['is_used']]

        for i in records:
            if i['is_used']:
                print(i)
                self.console.commands['watch'].watch_site(i['source'], site, outputs)

        # run watcher

        self.console.commands['watch'].file_monitor.start()
        self.console.commands['watch'].log()




        # self.console.watch(site, output, wait=False)
        self.console.commands['view'].stop()
        self.console.commands['view'].servers = []

        for i in records:

            self.console.commands['view'].start_server(i['output'], host, port)
            port = port + 1



        # self.console.view(site, host, port, output, wait=False, build=False)

        # Monitoring.
        self.event('before_waiting')

        while not self.stopped:
            time.sleep(config.wait_interval)

        return True


    def update(self, site, output):
        """Overwrites update method in watch command."""

        # Stop server here.
        # for i in self.console.commands['view'].servers:
        #     i.stop()

        # # Change to previous working directory.
        # cwd = os.getcwd()
        # os.chdir(self.cwd)

        # Run rebuild from watch command, but without triggering events.
        # self.console.commands['watch'].file_monitor.stop()
        records = self.console.commands['watch'].update(site, output, events=False)
        # self.console.commands['watch'].file_monitor.start()

        # Change to working directory to site output => server will serve from it.
        # os.chdir(cwd)



        # TODO: Remove server for dead sites.
        # TODO: Add servers for new sites.
        # Start server here.

        # for i in self.console.commands['view'].servers:
        #     i.restart()

        # self.console.commands['view'].server.restart()

        self.event('after_rebuild')


    def stop(self):
        """Stops command (stops development server and watcher)."""

        self.stopped = True
        