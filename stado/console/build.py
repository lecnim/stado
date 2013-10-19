"""Command: build"""

import os
import pkgutil

from . import Command, CommandError
from .. import log
from .. import config as CONFIG
from .. import utils


class Build(Command):
    """Builds site or group of sites."""

    name = 'build'

    usage = "build [site] [options]"
    summary = "Build the site in output directory."
    description = ''
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

            # List of directories in current working directory.
            cwd = os.getcwd()
            dirs = [i for i in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, i))]

            # No sites to build.
            if not dirs:
                log.info('Nothing to build, what about creating a new site?')

            for directory in dirs:
                if os.path.isdir(directory):

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


    def build_site(self, site: 'site directory'):
        """Returns imported site.py module from site directory."""

        path = os.path.join(os.getcwd(), site)

        if not os.path.exists(path):
            raise CommandError('Failed to build, site not found: ' + path)

        if self.is_site(path):

            log.info('Building site {}...'.format(site))
            timer = utils.Timer()

            # Import site.py
            for loader, module_name, is_pkg in pkgutil.iter_modules([path]):
                if module_name == 'site':
                    loader.find_module(module_name).load_module(module_name)

            log.info("Site built in {}s".format(timer.get()))
