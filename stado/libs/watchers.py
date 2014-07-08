"""
watchers.py

Monitors changes in the file system using watchers instances.

TODO: Better docstrings
TODO: Documentation

"""

import os
import sys
import threading
from stat import *
from collections import namedtuple

__version__ = '1.0.1-beta'

# Minimum python 3.2
if sys.hexversion < 0x030200F0:
    raise ImportError('Python < 3.2 not supported!')

# Python 3.2 do not support ns in os.stats!
PYTHON32 = True if sys.hexversion < 0x030300F0 else False
# Amount of time (in seconds) between running polling methods.
CHECK_INTERVAL = 2


class BaseWatcher:
    """Base watcher class."""

    def __init__(self, check_interval=None):

        self._is_alive = False
        self.lock = threading.Lock()
        self.check_thread = None

        if check_interval is None:
            self.check_interval = CHECK_INTERVAL
        else:
            self.check_interval = check_interval

    @property
    def is_alive(self):
        if self._is_alive \
           or (self.check_thread and self.check_thread.is_alive()):
            return True
        return False

    def check(self):
        """Override this."""
        pass

    def _thread_check(self):
        """Check runs by Timer thread."""

        self.check()
        self._start_timer_thread()

    def _start_timer_thread(self, check_interval=None):
        """Starts new Timer thread, it will run check after time interval."""

        # Lock pauses stop() method.
        # Check if watcher is alive because stop() can change it during
        # executing this method.
        with self.lock:
            if self._is_alive:

                if check_interval is None:
                    check_interval = self.check_interval

                self.check_thread = threading.Timer(check_interval,
                                                    self._thread_check)
                self.check_thread.name = repr(self)
                # self.check_thread.daemon = True
                self.check_thread.start()

    def start(self):
        """Starts watching. Returns False if the watcher is already started."""

        if self._is_alive:
            return False

        self._is_alive = True
        self._start_timer_thread(0)
        return True

    def stop(self):
        """Stops watching. Returns False if the watcher is already stopped."""

        if self._is_alive:

            # Lock prevents starting new Timer threads.
            with self.lock:
                self._is_alive = False
                self.check_thread.cancel()

            # Timer thread canceled, wait for join it.
            if threading.current_thread() != self.check_thread:
                self.check_thread.join()
            return True

        # Watcher already stopped.
        else:
            return False


# Watchers.

class Item:
    """Represents a file or a directory."""

    def __init__(self, path):

        # Path can be deleted during creating Item instance.
        self.path = path
        try:
            self.stat = os.stat(path)
        except (IOError, OSError):
            self.path = None

        if self.path:
            if S_ISDIR(self.stat.st_mode):
                self.is_file = False
            else:
                self.is_file = True

    def is_modified(self):
        """Returns True if a file/directory was modified."""

        # Path can be deleted before this method.
        try:
            stat = os.stat(self.path)
        except (IOError, OSError):
            return True

        if not self.is_file:
            # st_mode: File mode (permissions)
            # st_uid: Owner id.
            # st_gid: Group id.
            a = self.stat.st_mode, self.stat.st_uid, self.stat.st_gid
            b = stat.st_mode, stat.st_uid, stat.st_gid
            if a != b:
                self.stat = stat
                return True
            return False

        # Check if file is modified.
        a = self.stat.st_mtime, self.stat.st_size, self.stat.st_mode, \
            self.stat.st_uid, self.stat.st_gid
        b = stat.st_mtime, stat.st_size, stat.st_mode, stat.st_uid, stat.st_gid
        if a != b:
            self.stat = stat
            return True
        return False


class Watcher(BaseWatcher):
    """Watcher with events."""

    def __init__(self, path, recursive=False, filter=None, check_interval=None):
        super().__init__(check_interval)

        # Path must be always absolute!
        self.path = os.path.abspath(path)
        self.is_recursive = recursive

        # Callable which checks ignored paths.
        self.filter = filter
        self._events = {}

        # List of watched files, key is file path, value is Item instance.
        self.watched_paths = {}

        for path in self._walk():
            self.watched_paths[path] = Item(path)

    def __repr__(self):
        args = self.__class__.__name__, self.path, self.is_recursive
        return "{}(path={!r}, recursive={!r})".format(*args)

    def _walk(self):
        """Yields watched paths (already filtered)."""

        for path, dirs, files in os.walk(self.path):
            for i in dirs + files:
                p = os.path.join(path, i)
                if self.filter and not self.filter(p):
                    continue
                yield p
            if not self.is_recursive:
                break

    def check(self):
        """Detects changes in a file system. Returns True if something
        changed."""

        result = False
        stack = {}

        for path in self._walk():
            if self._path_changed(path, stack):
                result = True

        # Deleted paths.
        if self.watched_paths:
            for path in self.watched_paths.values():
                self.on_deleted(path)
                result = True

        self.watched_paths = stack
        return result

    def _path_changed(self, path, stack):
        """Checks if a path was modified or created."""

        # File exists and could be modified.
        if path in self.watched_paths:
            if self.watched_paths[path].is_file == os.path.isfile(path):

                x = self.watched_paths.pop(path)
                stack[path] = x

                if x.is_modified():
                    self.on_modified(x)
                    return True
                return False

        # Path was created.
        x = Item(path)
        if x.path:
            stack[path] = x
            self.on_created(x)
        return True

    # Events.

    def run_event(self, name):
        if name in self._events:
            event = self._events[name]
            event.callable(*event.args, **event.kwargs)

    def _add_event(self, name, callable, args, kwargs):
        Event = namedtuple('Event', 'callable args kwargs')
        self._events[name] = Event(callable, args, kwargs)

    def on_created(self, item, *args, **kwargs):
        if callable(item):
            self._add_event('on_created', item, args, kwargs)
        else:
            self.run_event('on_created')

    def on_modified(self, item, *args, **kwargs):
        if callable(item):
            self._add_event('on_modified', item, args, kwargs)
        else:
            self.run_event('on_modified')

    def on_deleted(self, item, *args, **kwargs):
        if callable(item):
            self._add_event('on_deleted', item, args, kwargs)
        else:
            self.run_event('on_deleted')


class SimpleWatcher(BaseWatcher):
    """A Watcher that runs callable when file system changed."""

    def __init__(self, path, target, args=(), kwargs=None, recursive=False,
                 filter=None, check_interval=None):
        super().__init__(check_interval)

        self.path = os.path.abspath(path)
        self.is_recursive = recursive
        self.filter = filter

        self.target = target
        self.args = args
        self.kwargs = {} if not kwargs else kwargs

        self.snapshot = self._get_snapshot()

    def __repr__(self):
        args = self.__class__.__name__, self.path, self.is_recursive
        return "{}(path={!r}, recursive={!r})".format(*args)

    def _get_snapshot(self):
        """Returns set with all paths in self.path."""

        snapshot = set()

        for path, dirs, files in os.walk(self.path):

            for i in dirs:
                if self.filter and not self.filter(os.path.join(path, i)):
                    continue

                p = os.path.join(path, i)
                try:
                    stats = os.stat(p)
                except (IOError, OSError):
                    pass
                else:
                    snapshot.add((
                        p,
                        stats.st_mode,
                        stats.st_uid,
                        stats.st_gid
                    ))

            for i in files:
                if self.filter and not self.filter(os.path.join(path, i)):
                    continue

                p = os.path.join(path, i)
                try:
                    stats = os.stat(p)
                except (IOError, OSError):
                    pass
                else:
                    snapshot.add((
                        p,
                        stats.st_mode,
                        stats.st_uid,
                        stats.st_gid,
                        stats.st_mtime if PYTHON32 else stats.st_mtime_ns,
                        stats.st_size
                    ))

            if not self.is_recursive:
                break
        return snapshot

    def check(self):
        """Detects changes in a file system. Returns True if something
        changed."""

        s = self._get_snapshot()
        if self.snapshot != s:
            self.target(*self.args, **self.kwargs)
            self.snapshot = s
            return True
        return False


class Manager(BaseWatcher):
    """Manager"""

    def __init__(self, check_interval=None):
        super().__init__(check_interval)

        self.watchers = set()
        self.watchers_lock = threading.Lock()

    def __repr__(self):
        args = self.__class__.__name__, self.check_interval
        return "{}(check_interval={!r})".format(*args)

    def add(self, watcher):
        """Adds a watcher to the manager."""

        if not watcher in self.watchers:

            # Adding to set is thread-safe?
            with self.watchers_lock:
                self.watchers.add(watcher)
            return True
        return False

    def remove(self, watcher):
        """Removes a watcher from the manager. Raises KeyError if a watcher is
        not in the manager watchers."""

        # Removing from set is thread-safe?
        with self.watchers_lock:
            try:
                self.watchers.remove(watcher)
            except KeyError:
                raise KeyError('Manager.remove(x): watcher x not in manager')
        return True

    def clear(self):
        """Removes all watchers."""

        with self.watchers_lock:
            self.watchers = set()

    def check(self):
        """Checks each watcher for changes in file system."""

        with self.watchers_lock:
            x = self.watchers.copy()

        # With this lock threads cannot modify self.watcher.
        for i in x:
            i.check()