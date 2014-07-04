"""Command: build"""

import os
import runpy

from . import Command, CommandError
from .. import log
from .. import utils
from .. import default_site, clear_default_site, Site


def build_site(path):
    """Runs python script file located in path, for example: 'path/to/file.py'.
     Also installs default site instance, so user can directly import
     controllers. Raises CommandError if path is not found."""

    cwd = os.getcwd()
    p = os.path.abspath(path)
    os.chdir(os.path.dirname(p))

    # Create default site as a shortcut.
    # Now you can directly import: "from stado import run, before"
    default_site(p)

    if not os.path.exists(p):
        raise CommandError('Failed to build, file not found: ' + path)

    log.info('Building site {}...'.format(path))
    timer = utils.Timer()

    try:
        runpy.run_path(p)
    except FileNotFoundError:
       raise CommandError('Failed to build, file not found: ' + path)

    log.info("Done! Site built in {}s".format(timer.get()))

    # Delete default site, so the next build will use new one.
    clear_default_site()
    os.chdir(cwd)


class Build(Command):
    """Run python module or package to build sites."""

    name = 'build'

    usage = "build [site] [options]\n    build [options]"
    summary = "Build the site or group of sites in output directory."
    description = ""
    options = []

    #

    def install(self, parser):
        """Add arguments to command line parser."""

        parser.add_argument('path', default=None, nargs='?')
        parser.set_defaults(function=self.run)

    def run(self, path=None):
        """Command-line interface will execute this method if user type 'build'
        command."""

        # Command run without arguments.
        # Run all python scripts in current working directory.
        if path is None:

            log.info('Searching python scripts...')

            files = [i for i in os.listdir('.') if
                     os.path.isfile(i) and i.endswith('.py')]

            # Build sites in alphabetical order, it is important when
            # development server is assigning ports.
            for i in sorted(files):
                build_site(i)

        else:
            # Path is pointing to python file.
            if os.path.isfile(path):
                build_site(path)
            # Path is pointing to directory, run all python scripts inside.
            else:

                log.info('Searching python scripts...')

                files = []
                for i in os.listdir(path):
                    fp = os.path.join(path, i)
                    if os.path.isfile(fp) and fp.endswith('.py'):
                        files.append(fp)

                for i in sorted(files):
                    build_site(i)

        # TODO: It always should return True?
        return True

    def build_path(self, path):
        Site._tracker.enable()
        self.run(path)
        return Site._tracker.dump(skip_unused=True)