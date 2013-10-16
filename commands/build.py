import os
from . import Command

class Build(Command):

    name = 'build'


    def run(self, project=None):

        # Path pointing to current working directory.
        cwd = os.getcwd()

        # Build all projects.
        if project is None:
            for directory in os.listdir(cwd):
                dir_path = os.path.join(cwd, directory)

                if self.is_site(dir_path):
                    # TODO: Import site.py module.
                    pass

        # Build only given project.
        else:
            if self.is_site(os.path.join(cwd, project)):
                # TODO: Import site.py module
                pass