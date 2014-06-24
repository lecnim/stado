"""Command: watch"""

import os
import time
import threading
import traceback

from . import Command, CommandError
from .build import Build
from .. import config, Site
from .. import log


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
        self.file_monitor = FileMonitor()
        # This function is run if watcher detected changes.
        self.update_function = self.update

    def install(self, parser):
        """Add arguments to command line parser."""

        parser.add_argument('path', default=None, nargs='?')
        parser.set_defaults(function=self.run)

    #

    @property
    def is_stopped(self):
        """Checks if command has stop running."""
        return False if self.file_monitor.is_enabled else True

    def run(self, path=None, stop_thread=True):
        """Command-line interface will execute this method if user type 'watch'
        command. Argument path is python script location,
        for example: 'path/to/file.py'. If argument stop_thread is True,
        current thread will be stopped in loop until file monitor is killed."""

        # Prevent multiple watcher thread!
        if self.file_monitor.is_enabled:
            raise CommandError('Command watch is already running! It must be '
                               'stopped before running it again')

        # Track every new created Site object.
        Site._tracker.enable()
        self.console.build(path)

        # List of every tracked Site object.
        records = Site._tracker.dump(skip_unused=True)
        # All output directories used by sites.
        outputs = {i['output'] for i in records}

        for i in records:
            # source: Absolute path to site source directory.
            # script: Absolute path to python script file.
            self.watch_site(i['script'], i['source'], outputs)

        self.log()

        # Monitoring.
        # New thread with file watcher is started here. This new thread will
        # run update() method if content of source directory was modified.

        if stop_thread:
            self.event('before_waiting')
        self.file_monitor.enable()

        # Wait here until watcher thread is not dead!
        while self.file_monitor.is_enabled and stop_thread is True:
            time.sleep(config.wait_interval)
        return True

    def log(self):
        """Log message."""

        log.info('Watching for changes...')
        for i in self.file_monitor.observers:
            log.debug('  Watching: {}'.format(i.path))
            for e in i.exclude:
                log.debug('    Exclude: {}'.format(e))

    def watch_site(self, script_path, source_path, output_paths):
        """Adds recursively all directories and files in source_path to watcher,
        excluding list of paths in output_path argument. After change in files,
        watcher will run python script located in script_path.

        Example arguments:
            script_path: 'path/to/file.py'
            source_path: 'path/to'
            output_paths: ['path/to/output']

        """

        self.file_monitor.watch(source_path, output_paths,
                                # This function will be run on rebuild.
                                self.update_function, script_path)

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

        # Track every new created Site object.
        Site._tracker.enable()

        try:
            self.console.build(script_path)

        # TODO: Better error message, now it is default python trackback.
        except Exception:
            # Remove gathered records, so next update will not use them.
            Site._tracker.dump()
            traceback.print_exc()

        else:
            records = Site._tracker.dump(skip_unused=True)
            outputs = {i['output'] for i in records}

            # Get all observers which must be updated.
            dead = {x for x in self.file_monitor.observers for y in records
                    if x.args[0] == y['script']}
            # Remove observer needed to be updated.
            for i in dead:
                self.file_monitor.observers.remove(i)
            # Add new updated.
            for i in records:
                self.watch_site(script_path, i['source'], outputs)

            self.log()

        if trigger_event:
            self.event('after_rebuild')

    def stop(self):
        """Stops watching.

        Important!
        This method start procedure of stopping watcher thread, so it can still
        execute some code after this method. Use file_monitor.is_stopped
        property to check if watcher thread is certainly dead!

        """

        log.debug('Stopping files watching...')
        self.file_monitor.disable()
        self.file_monitor.clear()


# File monitoring:

class Observer:
    """Used by FileMonitor. Observe given path and runs function when
    something was changed."""

    def __init__(self, path, exclude, function, args=(), kwargs={}):

        # Path is always absolute. If path is relative convert it to
        # absolute using current working directory.
        self.path = os.path.join(os.getcwd(), os.path.normpath(path))

        # List of paths that will be NOT watched.
        self.exclude = [os.path.join(self.path, os.path.normpath(i)) for i in exclude]

        # This function will be run when files changes.
        self.function = function
        self.args = args
        self.kwargs = kwargs

        # List of watched files, key is file path, value is modification time.
        self.watched_paths = {}

        for path, directories, files in os.walk(self.path):

            # Path can be excluded!
            if not self._is_excluded(path):
                self.watched_paths[path] = os.path.getmtime(path)
                for file in files:
                    fp = os.path.join(path, file)
                    self.watched_paths[fp] = os.path.getmtime(fp)

    def _is_excluded(self, path):
        """Returns True if path is excluded."""

        if path in self.exclude or [i for i in self.exclude if path.startswith(i)]:
            return True
        return False

    def run_function(self):
        """Runs stored function."""
        return self.function(*self.args, **self.kwargs)

    def check(self):
        """Checks if files were modified. If modified => runs function."""

        run_function = False

        # Current number of watched paths.
        number_of_paths = len(self.watched_paths)
        # Number of watched paths after check.
        i = 0

        for path, directories, files in os.walk(self.path):

            # Path can be excluded!
            if not self._is_excluded(path):
                # Directory was modified.
                i += 1
                if self.check_path(path):
                    run_function = True

                for file in files:
                    fp = os.path.join(path, file)
                    i += 1
                    if self.check_path(fp):
                        run_function = True

        # Some files were deleted, or created.
        if i != number_of_paths:
            return True
        return run_function

    def check_path(self, path):
        """Checks if path was modified, or created.

        Returns:
            True if path was modified or now created, False if not.
        """

        m_time = os.path.getmtime(path)     # Modification time.

        if path in self.watched_paths:
            # Path was modified.
            if m_time > self.watched_paths[path]:
                self.watched_paths[path] = m_time
                return True
            # Path was not modified.
            return False

        # Path was created.
        else:
            self.watched_paths[path] = m_time
            return True


class FileMonitor:
    """Watch for changes in files.

    Use watch() method to watch path (and everything inside it) and run given
    function when something changes.

    """

    def __init__(self):

        # Next check is run after this amount of time.
        self.interval = config.watch_interval

        self.observers = []
        self._enabled = False

        self.lock = threading.Lock()
        self.monitor = None             # Thread used for running self.check()

    @property
    def is_enabled(self):
        if (self.monitor and self.monitor.is_alive()) or self._enabled:
            return True
        return False

    def watch(self, path, exclude, function, *args, **kwargs):
        """Watches given path and run function when something changed."""

        observer = Observer(path, exclude, function, args, kwargs)
        self.observers.append(observer)
        return observer

    def _check(self):
        """Checks each observer. Runs by self.monitor thread."""

        with self.lock:
            if self._enabled:
                for i in self.observers[:]:
                    if i.check():
                        i.run_function()

                self.monitor = threading.Timer(self.interval, self._check)
                self.monitor.name = 'Watcher: ' + str(len(self.observers))
                self.monitor.daemon = True
                self.monitor.start()

    def disable(self):
        """Stops watching. Important: it do not clear observers, you can always
        use enable() to start watching again."""

        if self.monitor:
            self.monitor.cancel()
        self._enabled = False

    def enable(self):
        """Starts watching using observers."""

        self._enabled = True
        self._check()

    def clear(self):
        """Removes all observers."""

        self.observers = []
        if self.monitor:
            self.monitor.cancel()