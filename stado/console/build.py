"""Command: build"""

import os
import runpy
import gc

from . import Command, CommandError
from .. import log
from .. import config as CONFIG
from .. import utils
from .. import default_site, clear_default_site


class Build(Command):
    """Builds site or group of sites."""

    name = 'build'

    usage = "build [site] [options]\n    build [options]"
    summary = "Build the site or group of sites in output directory."
    description = ""
    options = [["-o, --output", "Specify the location to deploy to. (default: '{"
                                 "}')".format(CONFIG.build_dir)]]


    def install(self, parser):
        """Add arguments to command line parser."""

        parser.add_argument('site', default=None, nargs='?')
        parser.add_argument('--output', '-o')
        parser.set_defaults(function=self.run)


    def run(self, site=None, output=None):
        """Command-line interface will execute this method if user type 'build'
        command."""


        # Build all projects.
        if site is None:

            log.info('Searching sites...')

            # List of directories in current working directory.
            cwd = os.getcwd()
            dirs = [i for i in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, i))]

            # No sites to build.
            if not dirs:
                log.info('Nothing to build, what about creating a new site?')

            for directory in dirs:
                # Set custom output directory.
                if output: CONFIG.output = os.path.join(output, directory)
                self.build_site(directory)

        # Build only given project.
        else:
            # Set custom output directory.
            CONFIG.output = output
            self.build_site(site)

        # This is default output directory.
        CONFIG.output = None
        return True


    def build_site(self, site: 'site directory'):
        """Returns imported site.py module from site directory."""

        path = os.path.join(os.getcwd(), site)

        # Create default site as a shortcut.
        # Now you can directly import: "from stado import run, before"
        default_site(path)

        if not os.path.exists(path):
            raise CommandError('Failed to build, site not found: ' + path)

        if self.is_site(path):

            log.info('Building site {}...'.format(site))
            timer = utils.Timer()

            # Run site.py
            script_path = os.path.join(path, 'site.py')

            try:
                runpy.run_path(script_path)
            except FileNotFoundError:
               raise CommandError('Failed to build, file not found: ' + script_path)

            log.info("Done! Site built in {}s".format(timer.get()))

        else:
            log.info('Failed to build, file site.py not found in '
                     'directory: {}'.format(site))

        clear_default_site()
