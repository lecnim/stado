import os

from . import Command
from .build import Build
from utilities import copytree
from stado import config as CONFIG


class Deploy(Command):

    name = 'deploy'

    def install(self, parser):
        parser.add_argument('site', default=None, nargs='?')
        parser.add_argument('path')
        parser.set_defaults(function=self.run)


    def run(self, path, site=None):

        # Path pointing to current working directory.
        cwd = os.getcwd()

        # Deploy all projects.
        if site is None:
            for directory in os.listdir(cwd):
                dir_path = os.path.join(cwd, directory)
                self.deploy_site(dir_path, path)


        else:
            dir_path = os.path.join(cwd, site)
            self.deploy_site(dir_path, path)

    def deploy_site(self, source, destination):

        if self.is_site(source):

            build_path = os.path.join(source, CONFIG.build_dir)

            # Before deploying, site must be built already.
            if not os.path.exists(build_path):
                site_name = os.path.split(source)[1]
                Build().run(site_name)

            # Deploy.

            copytree(build_path, destination)
            return True
        return False
