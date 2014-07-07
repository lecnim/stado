"""Watch command."""

import os
import time
import traceback

from ..errors import CommandError
from ..events import Event
from .build import Build
from .. import config
from .. import log
from ...libs import watchers


class Watch(Build):
    """Builds a site and then monitor changes."""

    name = 'watch'
    usage = '{cmd} [path] [options]'
    summary = 'Build the site or group of sites and watch for changes.'

    #

    def __init__(self):
        super().__init__()

        # Yes, this object is watching for changes in files.
        self.file_monitor = watchers.Manager(check_interval=config.watch_interval)
        # This function is run if watcher detected changes.
        self.update_function = self._on_src_modified
        self._is_running = False

        self.src_watchers = set()

    # I Hate ARGPARSE:

    def _parser_add_arguments(self, parser):
        parser.add_argument('path', default=None, nargs='?', help='path')

    #

    @property
    def is_running(self):
        """Returns True if command is running."""

        if self.file_monitor.is_alive or self._is_running:
            return True
        return False

    def run(self, path=None, stop_thread=True):
        """A console use this method to run the command."""
        self.watch_path(path, stop_thread)

    # Public.

    def watch_path(self, path, stop_thread=True):

        self._run()

        try:
            site_records = self._build_path(path)
        except CommandError:
            self.cancel()
            raise
        except:
            traceback.print_exc()
            site_records = self._dump_tracker()

        path = os.path.abspath(path) if path else os.path.abspath('.')
        self._start_watching(path, site_records)

        if stop_thread:
            self.join()

        return True

    def watch_site(self, site, stop_thread=True):

        self._run()
        self._start_watching(site._script_path, [site.get_record()])

        if stop_thread:
            self.join()

        return True

    #

    def _run(self):

        # Prevent multiple watcher threads!
        if self.is_running:
            raise CommandError('Command watch is already running! It must be '
                               'stopped before running it again')
        self._is_running = True

    def _start_watching(self, path, site_records):
        """Creates watcher for each site. If path is pointing to package,
        creates package watcher too.

        Args:
            path: Path to a module file or a package directory.
            site_records: List of SiteRecords

        """

        # Monitor for new python scripts or deleted ones.
        if os.path.isfile(path):
            self._add_module_watcher(path)
        else:
            self._add_package_watcher(path)

        # Watch source dirs of Site instances.
        for i in site_records:
            self._add_src_watcher(i.module_path, i.source_path, i.output_path)

        self._log()

        # Monitoring.
        # New thread with file watcher is started here. This new thread will
        # run update() method if content of source directory was modified.
        self.file_monitor.start()


    def _add_module_watcher(self, path):

        w = watchers.Watcher(os.path.dirname(path),
                             recursive=False,
                             filter=lambda x: x == path)
        self._bind_module_events(w)
        self.file_monitor.add(w)

    def _add_package_watcher(self, path):

        def only_python(x):
            """Ignores all non-python files."""
            if os.path.isfile(x) and x.endswith('.py'):
                return True
            return False

        w = watchers.Watcher(path, recursive=False, filter=only_python)
        self._bind_module_events(w)
        self.file_monitor.add(w)

    def _bind_module_events(self, watcher):
        watcher.on_created = self._on_module_created
        watcher.on_deleted = self._on_module_deleted
        watcher.on_modified = self._on_module_modified


    def _add_src_watcher(self, module_path, source_path, output_path):
        """Adds recursively all directories and files in a source_path to
        a watcher, excluding a list of paths in an output_path argument.
        After change in files, a watcher will run a python script located in
        script_path.

        Example arguments:
            script_path: 'path/to/file.py'
            source_path: 'path/to'
            output_paths: ['path/to/output']

        """

        def filter(path):
            """Ignore:
            * All outputs.
            * Parent python script file.
            """
            if path in output_path \
               or [i for i in output_path if path.startswith(i + '/')] \
               or path == module_path:
                return False
            return True

        w = watchers.SimpleWatcher(source_path,
                                   self.update_function, args=(module_path,),
                                   filter=filter)
        w.script_path = module_path
        self.src_watchers.add(w)
        self.file_monitor.add(w)

    def _remove_src_watcher(self, module_path):

        for i in self.src_watchers.copy():
            if i.script_path == module_path:
                self.file_monitor.remove(i)
                self.src_watchers.remove(i)


    def _log(self):
        """Log current watchers."""

        log.info('\nWatching for changes...')
        for i in self.file_monitor.watchers:
            if isinstance(i, watchers.SimpleWatcher):
                log.debug('Script: {}'.format(i.args[0]))
                log.debug('  source: {}'.format(i.path))

    #
    # Command controls
    #

    def join(self):

        self.event(Event(self, 'on_wait'))

        # Wait here until a watcher thread is not dead!
        while self.is_running:
            if self.file_monitor.check_thread.is_alive():
                self.file_monitor.check_thread.join()

    def cancel(self):
        """Stops watching. It waits until a watch thread is dead."""

        if not self.is_running:
            raise CommandError('Watch: command already stopped!')

        log.debug('Stopping file watching service...')
        self.file_monitor.stop()
        self.file_monitor.clear()
        self.src_watchers.clear()

        self._is_running = False

    def pause(self):
        """Stops a file monitor."""

        if not self.is_running:
            raise CommandError(
                'Watch: cannot pause an already stopped command!')
        self.file_monitor.stop()

    def resume(self):
        """Un-pause a file monitor."""

        if not self._is_running:
            raise CommandError(
                'Watch: cannot resume an already stopped command!')
        self.file_monitor.start()

    def check(self):
        """Runs a file monitor check. Used during unittests!"""
        self.file_monitor.check()

    #
    # Watcher thread events:
    #
    # IMPORTANT!
    # This methods are always run in a Timer thread created by a file monitor,
    # a main thread is waiting in a wait loop in run() method.
    #

    # Watching scripts.

    def _on_module_created(self, item):
        """A new python script was created."""

        log.debug('Python module created: ' + item.path)
        try:
            records = self._build_path(item.path)
        except:
            traceback.print_exc()
            records = self._dump_tracker()

        for i in records:
            self._add_src_watcher(i.module_path, i.source_path, i.output_path)
        return records

    def _on_module_deleted(self, item):
        """A python script was deleted."""

        log.debug('Python module deleted: ' + item.path)
        self._remove_src_watcher(item.path)

    def _on_module_modified(self, item):
        """A python script was modified."""

        log.debug('Python module modified: ' + item.path)
        return self._on_src_modified(item.path)

    # Watching sources.

    def _on_src_modified(self, script_path):
        """Runs when source files of site were modified."""

        t = time.strftime('%H:%M:%S')
        log.info('{} - Rebuilding sites in: {}.'.format(t, script_path))

        # Script not exists, it was suddenly deleted.
        if not os.path.exists(script_path):
            return True, None

        try:
            records = self._build_path(script_path)
        except Exception as e:
            traceback.print_exc()
            return False, (e, traceback.format_exc())

        else:
            # Remove observer needed to be updated.
            for i in [i.module_path for i in records]:
                self._remove_src_watcher(i)
            # Add new updated watchers.
            for i in records:
                self._add_src_watcher(i.module_path, i.source_path, i.output_path)
            self._log()
            return True, records