"""Command: build"""

import os
import runpy
import gc

from . import Command, CommandError
from .. import log
from .. import config as CONFIG
from .. import utils
from .. import default_site, clear_default_site, Site


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

        parser.add_argument('path', default=None, nargs='?')
        parser.add_argument('--output', '-o')
        parser.set_defaults(function=self.run)


    def run(self, path=None, output=None):
        """Command-line interface will execute this method if user type 'build'
        command."""

        # Command run without arguments.
        # Run all python scripts in current working directory.
        if path is None:

            log.info('Searching sites...')

            files = [i for i in os.listdir('.') if
                     os.path.isfile(i) and i.endswith('.py')]

            # Build sites in alphabetical order, it is important when
            # development server is assigning ports.
            for i in sorted(files):
                self.build_site(i)


            # # List of directories in current working directory.
            # cwd = os.getcwd()
            # dirs = [i for i in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, i))]
            #
            # # No sites to build.
            # if not dirs:
            #     log.info('Nothing to build, what about creating a new site?')
            #
            # for directory in dirs:
            #     # Set custom output directory.
            #     if output: CONFIG.output = os.path.join(output, directory)
            #     try:
            #         self.build_site(directory)
            #     # Change output to default because other sites will use it
            #     #  instead of correct one.
            #     except:
            #         CONFIG.output = None
            #         raise

        # Build only given project.
        else:


            if os.path.isfile(path):
                self.build_site(path)

            else:




                files = [os.path.join(path, i) for i in os.listdir(path) if
                         os.path.isfile(os.path.join(path, i)) and os.path.join(path, i).endswith('.py')]

                for i in sorted(files):
                    self.build_site(i)
                # for i in os.listdir(path):
                #     fp = os.path.join(path, i)
                #     if os.path.isfile(fp) and fp.endswith('.py'):
                #         self.build_site(fp)


            # # Set custom output directory.
            # CONFIG.output = output
            # try:
            #     self.build_site(site)
            # # Change output to default because other sites will use it instead
            # # of correct one.
            # except:
            #     CONFIG.output = None
            #     raise

        # This is default output directory.
        CONFIG.output = None
        return True


    def build_site(self, site: 'site directory'):
        """Returns imported site.py module from site directory."""

        path = os.path.join(os.getcwd(), site)
        path = os.path.abspath(site)

        # Create default site as a shortcut.
        # Now you can directly import: "from stado import run, before"

        default_site(os.path.dirname(path))

        if not os.path.exists(path):
            raise CommandError('Failed to build, site not found: ' + path)

        if self.is_python_script(path):

            log.info('Building site {}...'.format(site))
            timer = utils.Timer()

            try:
                runpy.run_path(path, init_globals={'g':'hehe'})
            except FileNotFoundError:
               raise CommandError('Failed to build, file not found: ' + path)

            log.info("Done! Site built in {}s".format(timer.get()))

        else:
            log.info('Failed to build, file site.py not found in '
                     'directory: {}'.format(site))

        clear_default_site()
