import os
import pkgutil

from . import Command


class Build(Command):

    name = 'build'

    def install(self, parser):
        parser.add_argument('site', default=None, nargs='?')
        parser.set_defaults(function=self.run)

    def run(self, site=None):

        # Path pointing to current working directory.
        cwd = os.getcwd()

        # Build all projects.
        if site is None:
            for directory in os.listdir(cwd):
                dir_path = os.path.join(cwd, directory)

                if self.is_site(dir_path):
                    self._import_site(dir_path)

        # Build only given project.
        else:
            dir_path = os.path.join(cwd, site)
            if self.is_site(dir_path):
                self._import_site(dir_path)

    def _import_site(self, path):

        for loader, module_name, is_pkg in pkgutil.iter_modules([path]):
            if module_name == 'site':
                loader.find_module(module_name).load_module(module_name)