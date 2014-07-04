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
        parser.set_defaults(function=self.run)

        self.view = self.console.commands['view']
        self.watch = self.console.commands['watch']

    def run(self, site=None, host=None, port=None):
        """Command-line interface will execute this method if user type 'edit'
        command."""

        self.cwd = os.getcwd()
        self.stopped = False

        # Track Site instances.
        Site._tracker.enable()
        self.console.build(site)
        records = Site._tracker.dump(skip_unused=True)

        # Add build sites to watcher.
        watcher = self.console['watch']
        watcher.update_function = self.update
        # self.console.commands['watch'].file_monitor.disable()
        # self.console.commands['watch'].file_monitor.clear()
        # self.console.commands['watch'].event_update = self.update

        outputs = [i['output'] for i in records]
        for i in records:
            watcher.watch_site(i['script'], i['source'], outputs)

        # Run watcher.
        watcher.file_monitor.start()
        watcher.log()

        # self.console.commands['view'].stop()
        # self.console.commands['view'].servers = []

        # Run development servers.
        for i in records:
            self.console.commands['view'].start_server(i['output'], host, port)
            port = port + 1



        # self.console.view(site, host, port, output, wait=False, build=False)

        # Monitoring.
        self.event('before_waiting')

        while not self.is_stopped:
            time.sleep(config.wait_interval)

        print(watcher.file_monitor.check_thread.is_alive())
        print(threading.active_count())

        return True

    @property
    def is_stopped(self):
        if self.stopped and \
           self.console['watch'].is_stopped and \
           self.console['view'].is_stopped:
            return True
        return False


    def update(self, site):
        """Overwrites update method in watch command."""

        # Stop server here.
        # for i in self.console.commands['view'].servers:
        #     i.stop()

        # # Change to previous working directory.
        # cwd = os.getcwd()
        # os.chdir(self.cwd)

        # Run rebuild from watch command, but without triggering events.
        # self.console.commands['watch'].file_monitor.stop()
        records = self.console.commands['watch'].update(site, trigger_event=False)
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
        if not self.console['watch'].is_stopped:
            self.console['watch'].stop()
        self.console['view'].stop()

        