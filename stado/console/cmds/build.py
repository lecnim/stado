"""Build command."""

import os
import runpy
import errno

from . import Command
from ..errors import CommandError
from .. import log
from ... import utils
from ... import default_site, clear_default_site, Site


class Build(Command):
    """Run python module or package to build sites."""

    name = 'build'
    usage = '{cmd} [path] [options]'
    summary = "Build the site or group of sites in output directory."

    #

    def _parser_add_arguments(self, parser):
        parser.add_argument('path', default=None, nargs='?')

    #

    def run(self, path=None):
        """Command-line interface will execute this method if user type 'build'
        command."""

        self._build_path(path)
        return True

    def _build_path(self, path):
        """Runs a python module or package."""

        # Enable Sites instances tracking.
        self._track_sites()

        # Command run without arguments.
        # Run all python scripts in current working directory.
        if path is None: path = '.'

        # Path is pointing to python file.
        if os.path.isfile(path):
            self._run_modules(path)

        # Path is pointing to directory, run all python scripts inside.
        else:

            log.info('Searching python scripts...')

            try:
                listdir = os.listdir(path)
            # Support for Python 3.2
            except (IOError, OSError) as e:
                # File/dir not found.
                if e.errno == errno.ENOENT:
                    raise CommandError('Failed to build, path not found: ' + path)
                else:
                    raise
            else:

                files = []
                for i in listdir:
                    fp = os.path.join(path, i)
                    if os.path.isfile(fp) and fp.endswith('.py'):
                        files.append(fp)

                # Build sites in alphabetical order, it is important when
                # development server is assigning ports.
                self._run_modules(*files)

        return Site._tracker.dump(skip_unused=True)

    def _run_modules(self, *paths):

        # Python scripts not found!
        if not paths:
            log.info("Nothing to do here! What about creating a new site?")
            return False

        timer = utils.Timer()
        for i in sorted(paths):
            self._run_module(i)
        log.info("Done! Sites built in {}s".format(timer.get()))

    def _run_module(self, path):
        """Runs python script file located in path, for example: 'path/to/file.py'.
         Also installs default site instance, so user can directly import
         controllers. Raises CommandError if path is not found."""

        p = os.path.abspath(path)

        if not os.path.exists(p):
            raise CommandError('Failed to build, file not found: ' + path)
        if os.path.isdir(path):
            raise ValueError('Argument path must point to file, not dir!')

        cwd = os.getcwd()
        os.chdir(os.path.dirname(p))

        # Create default site as a shortcut.
        # Now you can directly import: "from stado import run, before"
        default_site(p)

        log.info('Building sites in {}...'.format(path))

        try:
            runpy.run_path(p)
        except:
            raise
        finally:
            # Delete default site, so the next build will use new one.
            clear_default_site()
            os.chdir(cwd)

    def _track_sites(self):
        """Stores basic info about each new Site instance."""
        Site._tracker.enable()

    def _dump_tracker(self, skip_unused=True):
        """Returns all basic info about tracked Site instances and clear
        tracker."""
        return Site._tracker.dump(skip_unused)