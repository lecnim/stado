"""Command: edit"""

import os
import time
import threading

from . import Command, Event, CommandError
from .. import config, Site, log
from .build import Build
from .watch import Watch
from .view import View


class Edit(Watch, View):

    name = 'edit'

    def __init__(self, build_cmd=None, watch_cmd=None, view_cmd=None):
        super().__init__()

    def run(self, path=None, host=None, port=None, stop_thread=True):
        """Command-line interface will execute this method if user type 'edit'
        command."""

        # Prevent multiple watcher thread!
        if not self.is_stopped:
            raise CommandError('Command edit is already running! It must be '
                               'stopped before running it again')

        self._is_stopped = False

        site_records = self.build_path(path)
        path = os.path.abspath(path) if path else os.path.abspath('.')
        self._run_watcher(path, site_records)
        self._start_servers(site_records, host, port)



        if stop_thread:
            self.event(Event(self, 'on_wait'))

            while not self.is_stopped:
                time.sleep(config.wait_interval)

        return True

    def pause_watcher(self):
        Watch.pause(self)

    def stop(self):
        """Stops command (stops development server and watcher)."""
        View.stop(self)
        Watch.stop(self)

        # # if not self.is_stopped:
        # #     raise CommandError('')
        #
        # self._is_stopped = True
        # print(self.watch_cmd.is_stopped)
        #
        # self.watch_cmd.stop()
        # self.view_cmd.stop()

    def _on_script_created(self, item):
        """A new python script was created."""
        records = Watch._on_script_created(self, item)

        for i in records:
            self._start_servers(records)

    def _on_script_deleted(self, item):
        """A python script was deleted."""

        Watch._on_script_deleted(self, item)

        if item.is_file:
            pass


    #
    # def _watch_src(self, script_path, source_path, output_paths):
    #
    #
    #
    #     Watch._watch_src(self, script_path, source_path, output_paths)
    #
    # def _unwatch_script(self, *script_paths):
    #     Watch._unwatch_script(*script_paths)






# class olfEdit(Command):
#     """Builds site, watches for changes and runs development server."""
#
#     name = 'edit'
#
#     # usage = 'edit [site] [options]'
#     # summary = 'Build the site, watch for changes and run development server.'
#     # description = ''
#     # options = View.options
#
#     def __init__(self, build_cmd=None, watch_cmd=None, view_cmd=None):
#         super().__init__()
#
#         if build_cmd is None: build_cmd = Build()
#         if watch_cmd is None: watch_cmd = Watch(build_cmd)
#         if view_cmd is None: view_cmd = View(build_cmd)
#
#         self.build_cmd = build_cmd
#         self.watch_cmd = watch_cmd
#         self.view_cmd = view_cmd
#
#         self._is_stopped = True
#
#         self.file_monitor = self.watch_cmd.file_monitor
#         self.servers = self.view_cmd.servers
#
#         self.watch_cmd.update_function = self.update
#
#     def install_in_parser(self, parser):
#         """Add arguments to command line parser."""
#
#         sub_parser = parser.add_parser(self.name, add_help=False)
#
#         sub_parser.add_argument('path', default=None, nargs='?')
#         sub_parser.add_argument('--port', '-p', type=int, default=config.port)
#         sub_parser.add_argument('--host', '-h', default=config.host)
#         sub_parser.set_defaults(function=self.run)
#
#         return sub_parser
#
#         # self.view = self.console.commands['view']
#         # self.watch = self.console.commands['watch']
#
#     def build(self, path):
#         return self.build_cmd.build_path(path)
#
#     def run(self, path=None, host=None, port=None, stop_thread=True):
#         """Command-line interface will execute this method if user type 'edit'
#         command."""
#
#         # Prevent multiple watcher thread!
#         if not self.is_stopped:
#             raise CommandError('Command edit is already running! It must be '
#                                'stopped before running it again')
#
#         self._is_stopped = False
#
#         site_records = self.build(path)
#         path = os.path.abspath(path) if path else os.path.abspath('.')
#         self.watch_cmd._run_watcher(path, site_records)
#         self.view_cmd._start_servers(site_records, host, port)
#
#
#
#         if stop_thread:
#             self.event(Event(self, 'on_wait'))
#
#             while not self.is_stopped:
#                 time.sleep(config.wait_interval)
#
#         return True
#
#
#
#     def pause(self):
#         """Stops a file monitor."""
#
#         if self.is_stopped:
#             raise CommandError(
#                 'Watch: cannot pause an already stopped command!')
#         self.watch_cmd.pause()
#         # self.view_cmd.pause()
#         # self.
#
#     def resume(self):
#         """Starts a file monitor again."""
#
#         if self._is_stopped:
#             raise CommandError(
#                 'Watch: cannot resume an already stopped command!')
#         self.file_monitor.start()
#
#     def check(self):
#         """Runs a file monitor check. Used during unittests!"""
#         self.watch_cmd.check()
#
#     @property
#     def is_stopped(self):
#         if self._is_stopped and \
#            self.watch_cmd.is_stopped and \
#            self.view_cmd.is_stopped:
#             return True
#         return False
#
#
#     def update(self, site):
#         """Overwrites update method in watch command."""
#
#
#         self.view_cmd.pause()
#
#         records = self.watch_cmd._on_rebuild(site)
#
#
#         self.view_cmd.resume()
#
#         # Script deleted
#         # Excpetion
#         # Ok
#
#
#
#
#     def stop(self):
#         """Stops command (stops development server and watcher)."""
#         print('TRY TO SOP')
#
#         # if not self.is_stopped:
#         #     raise CommandError('')
#
#         self._is_stopped = True
#         print(self.watch_cmd.is_stopped)
#
#         self.watch_cmd.stop()
#         self.view_cmd.stop()
#
#