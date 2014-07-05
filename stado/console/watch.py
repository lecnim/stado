"""Watch command."""

import os
import time
import traceback

from . import CommandError, Event
from .build import Build
from .. import config
from .. import log
from ..libs import watchers


class Watch(Build):
    """Builds a site and then monitor changes."""

    name = 'watch'
    usage = '{cmd} [path] [options]'
    summary = 'Build the site or group of sites and watch for changes.'

    #

    def __init__(self):
        super().__init__()

        # Yes, this object is watching for changes in files.
        self.file_monitor = watchers.Manager()
        # This function is run if watcher detected changes.
        self.update_function = self._on_src_modified
        self._is_running = False

    # I Hate ARGPARSE:

    def _parser_add_arguments(self, parser):
        parser.add_argument('path', default=None, nargs='?', help='path')

    #

    @property
    def is_running(self):
        """Returns True if command is running."""

        if self.file_monitor.is_alive:
            return True
        if self._is_running:
            return True
        return False

    def run(self, path=None, stop_thread=True):
        """Command-line interface will execute this method if user type 'watch'
        command. Argument path is python script location,
        for example: 'path/to/file.py'. If argument stop_thread is True,
        current thread will be stopped in loop until file monitor is killed."""

        # Prevent multiple watcher thread!
        if self.file_monitor.is_alive:
            raise CommandError('Command watch is already running! It must be '
                               'stopped before running it again')

        self._is_running = True

        # Track every new created Site object.
        # List of every tracked Site object.
        try:
            sites = self.build_path(path)
        except:
            traceback.print_exc()
            sites = self.dump_tracker()

        path = os.path.abspath(path) if path else os.path.abspath('.')
        self._run_watcher(path, sites)

        if stop_thread:
            self.event(Event(self, 'on_wait'))

            # Wait here until a watcher thread is not dead!
            while self.file_monitor.is_alive and stop_thread is True:
                time.sleep(config.wait_interval)

        return True

    def _run_watcher(self, path, site_records):
        """Creates watcher for each site. If path is pointing to package,
        creates package watcher too.

        Args:
            path: Path to a module file or a package directory.
            site_records: Dict created by Site._tracker.

        """

        # Monitor for new python scripts or deleted ones.
        self._watch_scripts(path)

        # Watch source dirs of Site instances.
        self._watch_sources(site_records)
        self._log()

        # Monitoring.
        # New thread with file watcher is started here. This new thread will
        # run update() method if content of source directory was modified.
        self.file_monitor.start()

    #
    # Command controls
    #

    def cancel(self):
        """Stops watching. It waits until a watch thread is dead."""

        if not self.is_running:
            raise CommandError('Watch: command already stopped!')

        log.debug('Stopping files watching...')
        self.file_monitor.stop()
        self.file_monitor.clear()

        self._is_running = False
        log.debug('Done!')

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

    # Private!

    def _log(self):
        """Log current watchers."""

        log.info('Watching for changes...')
        for i in self.file_monitor.watchers:
            if isinstance(i, watchers.SimpleWatcher):
                log.debug('  Script: {}'.format(i.args[0]))
                log.debug('    source: {}'.format(i.path))

    def _watch_scripts(self, path):
        """Creates a watcher that monitor python script files."""

        # Monitor an every change of python scripts in directory.
        if os.path.isdir(path):

            def only_python(x):
                """Ignores all non-python files."""
                if os.path.isfile(x) and x.endswith('.py'):
                    return True
                return False
            w = watchers.Watcher(path, recursive=False, filter=only_python)

        # Monitor changes in given python script.
        else:
            w = watchers.Watcher(os.path.dirname(path), recursive=False,
                                 filter=lambda x: x == path)

        # Monkey path Watcher events!
        w.on_created = self._on_script_created
        w.on_deleted = self._on_script_deleted
        w.on_modified = self._on_script_modified
        # Watcher is not connected with any script file.
        w.script_path = None
        self.file_monitor.add(w)

    def _watch_sources(self, site_records):
        """Creates a watcher that monitors each source directory."""

        # All output directories used by sites.
        outputs = {i['output'] for i in site_records}

        for site in site_records:
            # source: Absolute path to site source directory.
            # script: Absolute path to python script file.
            self._watch_src(site['script'], site['source'], outputs)

    def _watch_src(self, script_path, source_path, output_paths):
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
            if path in output_paths \
               or [i for i in output_paths if path.startswith(i + '/')] \
               or path == script_path:
                return False
            return True

        w = watchers.SimpleWatcher(source_path,
                                   self.update_function, args=(script_path,),
                                   filter=filter)
        w.script_path = script_path
        self.file_monitor.add(w)

    def _unwatch_sources(self, *script_paths):
        """Removes all watchers that are watching a script source."""

        dead = [i for i in self.file_monitor.watchers
                if i.script_path in script_paths]
        for i in dead:
            self.file_monitor.remove(i)

    #
    # Watcher thread events:
    #
    # IMPORTANT!
    # This methods are always run in a Timer thread created by a file monitor,
    # a main thread is waiting in a wait loop in run() method.
    #

    # Watching scripts.

    def _on_script_created(self, item):
        """A new python script was created."""

        log.debug('Script created: ' + item.path)
        try:
            records = self.build_path(item.path)
        except:
            traceback.print_exc()
            records = self.dump_tracker()
        self._watch_sources(records)
        return records

    def _on_script_deleted(self, item):
        """A python script was deleted."""
        log.debug('Script deleted: ' + item.path)
        self._unwatch_sources(item.path)

    def _on_script_modified(self, item):
        """A python script was modified."""
        log.debug('Script modified: ' + item.path)
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
            records = self.build_path(script_path)
        except Exception as e:
            traceback.print_exc()
            return False, (e, traceback.format_exc())

        else:
            # Remove observer needed to be updated.
            self._unwatch_sources(*[i['script'] for i in records])
            # Add new updated watchers.
            self._watch_sources(records)
            self._log()
            return True, records