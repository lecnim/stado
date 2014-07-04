"""Command: edit"""

import os
import time
import threading

from . import Command
from .. import config, Site
from .build import Build
from .watch import Watch
from .view import View


class Edit(Command):
    """Builds site, watches for changes and runs development server."""

    name = 'edit'

    # usage = 'edit [site] [options]'
    # summary = 'Build the site, watch for changes and run development server.'
    # description = ''
    # options = View.options

    def __init__(self, build_cmd=None, watch_cmd=None, view_cmd=None):

        if build_cmd is None: build_cmd = Build()
        if watch_cmd is None: watch_cmd = Watch(build_cmd)
        if view_cmd is None: View(build_cmd)

        self.build_cmd = build_cmd
        self.watch_cmd = watch_cmd
        self.view_cmd = view_cmd

        self.stopped = True
        self.cwd = None

    def install_in_parser(self, parser):
        """Add arguments to command line parser."""

        sub_parser = parser.add_parser(self.name, add_help=False)

        sub_parser.add_argument('site', default=None, nargs='?')
        sub_parser.add_argument('--port', '-p', type=int, default=config.port)
        sub_parser.add_argument('--host', '-h', default=config.host)
        sub_parser.set_defaults(function=self.run)

        return sub_parser

        # self.view = self.console.commands['view']
        # self.watch = self.console.commands['watch']

    def build(self, path):
        return self.build_cmd.build_path(path)

    def run(self, site=None, host=None, port=None, stop_thread=True):
        """Command-line interface will execute this method if user type 'edit'
        command."""

        self.cwd = os.getcwd()
        self.stopped = False

        # Track Site instances.
        records = self.build(site)

        # Add build sites to watcher.
        self.watch_cmd.update_function = self.update

        outputs = [i['output'] for i in records]
        for i in records:
            self.watch_cmd.watch_site(i['script'], i['source'], outputs)

        # Run watcher.
        self.watch_cmd.file_monitor.start()
        self.watch_cmd.log()

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

        