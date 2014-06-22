"""Command: watch"""

import os
import sys
import time
import threading
import datetime
import traceback

from . import Command, CommandError
from .build import Build
from .. import config, Site
from .. import log


class Watch(Command):
    """Watches for changes and rebuilds site."""

    name = 'watch'

    usage = 'watch [site] [options]\n    watch [options]'
    summary = 'Build the site or group of sites and watch for changes.'
    description = ''
    options = Build.options


    def __init__(self, command_line):
        Command.__init__(self, command_line)

        self.file_monitor = FileMonitor()


    def install(self, parser):
        """Add arguments to command line parser."""

        parser.add_argument('site', default=None, nargs='?')
        parser.add_argument('--output', '-o')
        parser.set_defaults(function=self.run)


    def run(self, site=None, output=None, wait=True):
        """Command-line interface will execute this method if user type 'watch'
        command."""

        path = site

        # Watch only given site.
        if site:
            path = os.path.abspath(site)

        Site._tracker.enable()
        self.console.build(path, output)

        records = Site._tracker.dump(skip_unused=True)
        outputs = [i['output'] for i in records if i['is_used']]

        for i in records:
            if i['is_used']:
                self.watch_site(i['source'], site, outputs)


        # Monitoring.
        print(self.file_monitor.observers)
        log.debug('MONITOR START')
        self.file_monitor.start()
        if wait: self.event('before_waiting')

        self.log()


        while not self.file_monitor.stopped and wait is True:
            time.sleep(config.wait_interval)

        return True

    def log(self):
        log.info('Watching for changes...')
        for i in self.file_monitor.observers:
            log.debug('  Watching: {}'.format(i.path))
            log.debug('  Args: {}'.format(i.args))
            for e in i.exclude:
                log.debug('    Exclude: {}'.format(e))


    def watch_site(self, path, site, output=None):
        """Add site files to file monitor."""

        # Exclude output directory to prevent rebuild looping.
        if output:
            if isinstance(output, str):
                exclude = [output]
            else:
                exclude = output
        else:
            exclude = [os.path.join(path, config.build_dir)]

        self.file_monitor.watch(path, exclude, self.event_update, site, output)


    def event_update(self, site, output):
        self.update(site, output)

    def update(self, site, output, events=True):
        """This method is run by file monitor each time when files in source
        directory of site were modified.

        IMPORTANT!
        This method is always run in Timer thread, main thread is waiting in
        wait loop.


        """

        t = time.strftime('%H:%M:%S')
        log.info('{} - Rebuilding site: {}.'.format(t, site))

        Site._tracker.enable()

        try:
            self.console.build(site, output)
            # self.file_monitor.start()

        # TODO: Better error message, now it is default python trackback.
        # except Exception as error:
        #     Site._tracker.dump(skip_unused=True)
        #     traceback.print_exc()
        except:
            raise
        else:

            records = Site._tracker.dump(skip_unused=True)
            outputs = [i['output'] for i in records if i['is_used']]

            self.file_monitor.observers = []

            for i in records:
                if i['is_used']:
                    self.watch_site(i['source'], site, outputs)

            self.log()


        if events:
            self.event('after_rebuild')

        return records


    def stop(self):
        """Stop watching."""

        log.debug('Files watching stopped.')
        self.file_monitor.stop()



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

        log.debug('CHECK' + str(threading.current_thread()))

        with self.lock:
            if not self.stopped:

                for i in self.observers[:]:
                    if i.check():
                        log.debug('MODIFIED' + i.path)
                        i.run_function()
                    else:
                        log.debug('NOT MODIFIED' + i.path)

                self.monitor = threading.Timer(self.interval, self.check)
                self.monitor.name = 'Watcher' + str(len(self.observers))
                self.monitor.daemon = True
                self.monitor.start()

    def stop(self):
        """Stop watching."""

        if self.monitor:
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
