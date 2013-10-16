import os
from . import Command
from .build import Build

class Deploy(Command):

    name = 'deploy'

    def run(self, path, project=None):

        # Path pointing to current working directory.
        cwd = os.getcwd()

        # Deploy all projects.
        if project is None:
            for directory in os.listdir(cwd):
                dir_path = os.path.join(cwd, directory)
                self._deploy_site(dir_path, directory)


        else:
            dir_path = os.path.join(cwd, project)
            self._deploy_site(dir_path, project)

    def _deploy_site(self, path, project):

        if self.is_site(path):
            build_path = os.path.join(path, '_build')

            # Build project first.
            if not os.path.exists(build_path):
                Build().run(project)

            # TODO: copy build directory to path