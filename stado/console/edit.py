"""Command: edit"""

import os
import time
import traceback

from . import Event, CommandError
from .. import config, log
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
        if self.is_running:
            raise CommandError('Command edit is already running! It must be '
                               'stopped before running it again')

        self._is_running = True

        try:
            site_records = self.build_path(path)
        except Exception:
            site_records = self.dump_tracker()
            traceback.print_exc()

        path = os.path.abspath(path) if path else os.path.abspath('.')
        self._run_watcher(path, site_records)
        self._start_servers(site_records, host, port)

        if stop_thread:
            self.event(Event(self, 'on_wait'))

            while self.is_running:
                time.sleep(config.wait_interval)

        return True

    def pause_watcher(self):
        Watch.pause(self)

    def stop(self):
        """Stops command (stops development server and watcher)."""
        View.stop(self)
        Watch.stop(self)

    def _on_script_created(self, item):
        """A new python script was created."""
        records = Watch._on_script_created(self, item)

        self._start_servers(records)

    def _on_script_deleted(self, item):
        """A python script was deleted."""

        Watch._on_script_deleted(self, item)

        dead = [i for i in self.servers if i.script_path == item.path]
        for i in dead:
            self._stop_server(i)

    def _on_src_modified(self, script_path):


        View.pause(self)
        ok, data = Watch._on_src_modified(self, script_path)
        View.resume(self)

        if ok and data:
            self._stop_servers(data)
            self._start_servers(data)

        if not ok:

            exception, tb = data

            for i in self.servers:
                if i.script_path == script_path:
                    i.set_exception(tb)
