import os
import pkgutil

from . import Command
from stado import config as CONFIG


class Build(Command):

    name = 'build'

    def install(self, parser):
        parser.add_argument('site', default=None, nargs='?')
        parser.add_argument('--output', '-o')
        parser.set_defaults(function=self.run)


    def run(self, site=None, output=None):
        """Command-line interface will execute this method if user type 'build'
        command."""

        # Run user interface event.
        self.user_interface.before_build()

        # Build all projects.
        if site is None:
            for directory in os.listdir(os.getcwd()):

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

        # Run user interface event.
        self.user_interface.after_build()


    def build_site(self, site: 'site directory'):
        """Returns imported site.py module from site directory."""

        path = os.path.join(os.getcwd(), site)
        if self.is_site(path):

            # Import site.py
            for loader, module_name, is_pkg in pkgutil.iter_modules([path]):
                if module_name == 'site':
                    return loader.find_module(module_name).load_module(module_name)
