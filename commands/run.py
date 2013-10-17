import os
import threading
from . import Command
from .build import Build
from stado import config as CONFIG



# File monitoring:

class Observer:
    """Used by FileMonitor. Observe given path and runs function when
    something was changed."""

    def __init__(self, path, exclude, function, args, kwargs):

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
        self.watched = {}

        for path, directories, files in os.walk(self.path):

            # Path can be excluded!
            if not self._is_excluded(path):
                self.watched[path] = os.path.getmtime(path)
                for file in files:
                    fp = os.path.join(path, file)
                    self.watched[fp] = os.path.getmtime(fp)

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

        for path, directories, files in os.walk(self.path):

            # Path can be excluded!
            if not self._is_excluded(path):
                # Directory was modified.
                if self.check_path(path):
                    run_function = True

                for file in files:
                    fp = os.path.join(path, file)
                    if self.check_path(fp):
                        run_function = True

        return run_function

    def check_path(self, path):
        """Checks if path was modified, or created.

        Returns:
            True if path was modified or now created, False if not.
        """

        m_time = os.path.getmtime(path)     # Modification time.

        if path in self.watched:
            # Path was modified.
            if m_time > self.watched[path]:
                self.watched[path] = m_time
                return True
            # Path was not modified.
            return False

        # Path was created.
        else:
            self.watched[path] = m_time
            return True


class FileMonitor:

    """Watch for changes in files.

    Use watch() method to watch path (and everything inside it) and run given
    function when something changes.

    """

    def __init__(self):

        self.interval = 2

        self.observers = []
        self.stopped = True

        self.lock = threading.Lock()
        self.monitor = None             # Thread used for running self.check()

    def watch(self, path, exclude, function, *args, **kwargs):
        """Watches given path and run function when something changed."""

        observer = Observer(path, exclude, function, args, kwargs)
        self.observers.append(observer)
        return observer

    def check(self):
        """Checks each observer. Runs by self.monitor thread."""

        with self.lock:
            if not self.stopped:

                for i in self.observers[:]:
                    if i.check(): i.run_function()

                self.monitor = threading.Timer(self.interval, self.check)
                self.monitor.daemon = True
                self.monitor.start()

    def stop(self):
        """Stop watching."""
        self.monitor.cancel()
        self.stopped = True

    def start(self):
        """Start watching."""
        self.stopped = False
        self.check()

    def clear(self):
        """Removes all observers."""
        self.observers = []
        if self.monitor:
            self.monitor.cancel()


class Run(Command):

    name = 'run'

    def __init__(self, user_interface):
        Command.__init__(self, user_interface)

        self.watcher = FileMonitor()

    def run(self, site=None):

        # Build site / sites
        cmd = 'build' if site is None else 'build ' + site
        self.user_interface.call(cmd)

        # Watcher.
        if site:
            site_path = os.path.join(os.getcwd(), site)
            exclude = os.path.join(site_path, CONFIG.build_dir)
            self.watcher.watch(site_path, exclude, self.update)



    def update(self):
        pass



