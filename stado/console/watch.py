"""Command: watch"""

import os
import time
import traceback

from . import Command, CommandError, Event
from .build import Build
from .. import config
from .. import log
from ..libs import watchers



class Watch(Build):
    """Builds site and then watches for file changes and rebuilds it."""

    name = 'watch'

    # usage = 'watch [site] [options]\n    watch [options]'
    # summary = 'Build the site or group of sites and watch for changes.'
    # description = ''
    # options = Build.options

    #

    def __init__(self, build_cmd=None):
        super().__init__()

        # Default build command.
        if build_cmd is None: build_cmd = Build()
        self.build_cmd = build_cmd

        # Yes, this object is watching for changes in files.
        # self.file_monitor = FileMonitor()
        self.file_monitor = watchers.Manager()
        # This function is run if watcher detected changes.
        self.update_function = self._on_rebuild

        self._is_stopped = True

    def install_in_parser(self, parser):
        """Add arguments to command line parser."""

        sub_parser = parser.add_parser(self.name, add_help=False)
        sub_parser.add_argument('path', default=None, nargs='?')
        sub_parser.set_defaults(function=self.run)
        return sub_parser

    #

    @property
    def is_stopped(self):
        """Checks if command has stop running."""

        # return True if self._is_stopped and not self.file_monitor.is_alive else False

        if self.file_monitor.is_alive:
            return False
        if not self._is_stopped:
            return False
        return True
        #
        # return False if not self._is_stopped \
        #                 or self.file_monitor.is_alive else True

    def run(self, path=None, stop_thread=True):
        """Command-line interface will execute this method if user type 'watch'
        command. Argument path is python script location,
        for example: 'path/to/file.py'. If argument stop_thread is True,
        current thread will be stopped in loop until file monitor is killed."""

        # Prevent multiple watcher thread!
        if self.file_monitor.is_alive:
            raise CommandError('Command watch is already running! It must be '
                               'stopped before running it again')

        self._is_stopped = False

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

    def stop(self):
        """Stops watching. It waits until a watch thread is dead."""

        # if self.is_stopped:
        #     raise CommandError('Watch: command already stopped!')

        log.debug('Stopping files watching...')
        self.file_monitor.stop()
        self.file_monitor.clear()

        self._is_stopped = True
        log.debug('Done!')

    def pause(self):
        """Stops a file monitor."""

        if self.is_stopped:
            raise CommandError(
                'Watch: cannot pause an already stopped command!')
        self.file_monitor.stop()

    def resume(self):
        """Starts a file monitor again."""

        if self._is_stopped:
            raise CommandError(
                'Watch: cannot resume an already stopped command!')
        self.file_monitor.start()

    def check(self):
        """Runs a file monitor check. Used during unittests!"""
        print('check')
        self.file_monitor.check()

    # Private!

    def _log(self):
        """Log current watchers."""

        log.info('Watching for changes...')
        for i in self.file_monitor.watchers:
            if isinstance(i, watchers.SimpleWatcher):
                log.debug('  Script: {}'.format(i.args[0]))
                log.debug('    source: {}'.format(i.path))

    # def _build(self, path):
    #     """Shortcut for build method in Build commad."""
    #     return self.build_cmd.build_path(path)

    def _watch_scripts(self, path):
        """Creates a watcher that monitor python script files."""

        # Monitor every change in python scripts in directory.
        if os.path.isdir(path):
            w = watchers.Watcher(path, recursive=False,
                                 filter=lambda x: x.endswith('.py'))
        # Monitor changes in given python script.
        else:
            def f(x):
                print(x, path)
                return x == path
            w = watchers.Watcher(os.path.dirname(path), recursive=False,
                                 filter=f)

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
                print('FALSE', path)
                return False
            return True

        w = watchers.SimpleWatcher(source_path,
                                   self.update_function, args=(script_path,),
                                   filter=filter)
        w.script_path = script_path
        self.file_monitor.add(w)

    def _unwatch_script(self, *script_paths):
        """Removes all watchers that are watching a script."""

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

        if item.is_file:
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

        if item.is_file:
            log.debug('Script deleted: ' + item.path)
            self._unwatch_script(item.path)

    def _on_script_modified(self, item):
        """A python script was modified."""

        if item.is_file:
            log.debug('Script modified: ' + item.path)
            return self._on_rebuild(item.path)

    # Watching sources.

    def _on_rebuild(self, script_path):
        """This method is run by file monitor each time when files in source
        directory of site were modified. If argument trigger_event is True,
        event 'after_rebuild' will be executed at the end of this method."""

        t = time.strftime('%H:%M:%S')
        log.info('{} - Rebuilding sites in: {}.'.format(t, script_path))

        # Script not exists: remove all connected watchers.
        if not os.path.exists(script_path):
            log.debug('Rebuild Script deleted: ' + script_path)
            # self._unwatch_script(script_path)
            return True, []

        try:
            records = self.build_path(script_path)

        # TODO: Better error message, now it is default python trackback.
        except Exception as e:
            traceback.print_exc()
            # traceback.
            return False, (e, traceback.format_exc())

        else:
            # Remove observer needed to be updated.
            self._unwatch_script(*[i['script'] for i in records])

            # Add new updated watchers.
            self._watch_sources(records)
            self._log()
            return True, records

            # True, site_records