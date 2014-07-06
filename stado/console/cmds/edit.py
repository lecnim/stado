"""Edit command."""

import os
import time
import traceback

from ..errors import CommandError
from .watch import Watch
from .view import View
from ..events import Event

from .. import config



class Edit(Watch, View):
    """Build a site, monitor changes, starts development server."""

    name = 'edit'
    usage = '{cmd} [path] [options]'
    summary = 'Build the site, watch for changes and run development server.'

    def run(self, path=None, host=None, port=None, stop_thread=True):
        """Command-line interface will execute this method if user type 'edit'
        command."""

        # Prevent multiple watcher thread!
        if self.is_running:
            raise CommandError('Command edit is already running! It must be '
                               'stopped before running it again')

        self._is_running = True

        try:
            site_records = self._build_path(path)
        except Exception:
            site_records = self._dump_tracker()
            traceback.print_exc()

        path = os.path.abspath(path) if path else os.path.abspath('.')
        self._start_servers(site_records, host, port)
        self._run_watcher(path, site_records)

        if stop_thread:
            self.event(Event(self, 'on_wait'))

            while self.is_running:
                time.sleep(config.wait_interval)

        return True

    def pause_watch(self):
        """Pauses the file monitor."""
        Watch.pause(self)

    def cancel(self):
        """Stops command - stops development server and watcher."""
        View.cancel(self)
        Watch.cancel(self)

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
        """A python script was modified."""

        # Pause development servers - prevents threads concurrency.
        View.pause(self)
        ok, data = Watch._on_src_modified(self, script_path)
        View.resume(self)

        # ok: True
        # data: Site records.
        if ok and data:
            port = self._stop_servers(data)
            self._start_servers(data, port=port)

        if not ok:
            exception, tb = data
            # An exception occurred, set servers to error mode.
            for i in self.servers:
                if i.script_path == script_path:
                    i.set_error(tb)