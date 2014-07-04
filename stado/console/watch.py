"""Command: watch"""

import os
import time
import threading
import traceback
import fnmatch

from contextlib import contextmanager

from . import Command, CommandError
from .build import Build
from .. import config, Site
from .. import log
from ..libs import watchers


class Watch(Command):
    """Builds site and then watches for file changes and rebuilds it."""

    name = 'watch'

    usage = 'watch [site] [options]\n    watch [options]'
    summary = 'Build the site or group of sites and watch for changes.'
    description = ''
    options = Build.options

    #

    def __init__(self, command_line):
        super().__init__(command_line)

        # Yes, this object is watching for changes in files.
        # self.file_monitor = FileMonitor()
        self.file_monitor = watchers.Manager()
        # This function is run if watcher detected changes.
        self.update_function = self.update

        self._is_stopped = True

    def install(self, parser):
        """Add arguments to command line parser."""

        parser.add_argument('path', default=None, nargs='?')
        parser.set_defaults(function=self.run)

    def build(self, path):
        return self.console.commands['build'].build_path(path)

    #

    @property
    def is_stopped(self):
        """Checks if command has stop running."""
        return False if not self._is_stopped \
                        or self.file_monitor.is_alive else True

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
        if path is None: path = '.'

        # Track every new created Site object.
        # List of every tracked Site object.
        records = self.build(path)
        # All output directories used by sites.
        outputs = {i['output'] for i in records}

        for i in records:
            # source: Absolute path to site source directory.
            # script: Absolute path to python script file.
            self.watch_site(i['script'], i['source'], outputs)

        # Monitor path for new python scripts or deleted ones.
        if os.path.isdir(path):
            w = watchers.Watcher(path, recursive=False)
            w.on_created = self.on_script_created
            w.on_deleted = self.on_script_deleted
            w.script_path = None
            self.file_monitor.add(w)

        self.log()

        # Monitoring.
        # New thread with file watcher is started here. This new thread will
        # run update() method if content of source directory was modified.
        #
        # if stop_thread:
        #     self.event('before_waiting')
        self.file_monitor.start()

        # self.console.on_run_watch(self)

        # Wait here until a watcher thread is not dead!
        while self.file_monitor.is_alive and stop_thread is True:
            time.sleep(config.wait_interval)

        return True

    #
    # Command controls
    #

    def stop(self):
        """Stops watching. It waits until a watch thread is dead."""

        if self.is_stopped:
            raise CommandError('Watch: command already stopped!')

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
        self.file_monitor.check()

    #

    def log(self):
        """Log current watchers."""

        log.info('Watching for changes...')
        for i in self.file_monitor.watchers:
            if isinstance(i, watchers.SimpleWatcher):
                log.debug('  Script: {}'.format(i.args[0]))
                log.debug('    source: {}'.format(i.path))

    def watch_site(self, script_path, source_path, output_paths):
        """Adds recursively all directories and files in source_path to watcher,
        excluding list of paths in output_path argument. After change in files,
        watcher will run python script located in script_path.

        Example arguments:
            script_path: 'path/to/file.py'
            source_path: 'path/to'
            output_paths: ['path/to/output']

        """

        filter = lambda path: False if path in output_paths \
            or [i for i in output_paths if path.startswith(i + '/')] else True

        w = watchers.SimpleWatcher(source_path,
                                   self.update_function, args=(script_path,),
                                   filter=filter)
        w.script_path = script_path
        self.file_monitor.add(w)

    def kill_watchers(self, *script_paths):
        """Removes all watchers that are watching a script."""

        dead = [i for i in self.file_monitor.watchers
                if i.script_path in script_paths]
        for i in dead:
            self.file_monitor.remove(i)

    #
    # Watcher thread events:
    #

    def on_script_created(self, item):
        """A new python script was created in the package."""

        if item.is_file and item.path.endswith('.py'):

            log.debug('Script created: ' + item.path)

            records = self.build(item.path)
            outputs = {i['output'] for i in records}
            # Add new updated.
            for i in records:
                self.watch_site(item.path, i['source'], outputs)

    def on_script_deleted(self, item):
        """A python script was deleted from the package."""

        if item.is_file and item.path.endswith('.py'):
            log.debug('Script deleted: ' + item.path)
            self.kill_watchers(item.path)

    def update(self, script_path, trigger_event=True):
        """This method is run by file monitor each time when files in source
        directory of site were modified. If argument trigger_event is True,
        event 'after_rebuild' will be executed at the end of this method.

        IMPORTANT!
        This method is always run in Timer thread created by file monitor,
        main thread is waiting in wait loop in run() method.

        """

        t = time.strftime('%H:%M:%S')
        log.info('{} - Rebuilding sites in: {}.'.format(t, script_path))

        # Script not exists: remove all connected watchers.
        if not os.path.exists(script_path):
            log.debug('Script deleted: ' + script_path)
            self.kill_watchers(script_path)
            return False

        try:
            records = self.build(script_path)

        # TODO: Better error message, now it is default python trackback.
        except Exception:
            traceback.print_exc()
            return False

        else:
            # Remove observer needed to be updated.
            self.kill_watchers(*[i['script'] for i in records])

            # Add new updated watchers.
            outputs = {i['output'] for i in records}
            for i in records:
                self.watch_site(script_path, i['source'], outputs)

            self.log()
            return True