import os

class Command:

    name = ''
    summary = ''

    def install(self, parser):
        return parser

    def run(self, *args, **kwargs):
        pass


    @staticmethod
    def is_site(path):

        if os.path.isdir(path) and 'site.py' in os.listdir(path):
            return True
        return False


import sys
import argparse


from .build import Build
from .deploy import Deploy
from .view import View
from .run import Run


class UserInterface:

    def __init__(self):

        # Available commands.

        self.commands = {
            Build.name: Build(),
            Deploy.name: Deploy(),
            View.name: View(),
            Run.name: Run()
        }

        # Create command line parser.

        self.parser = argparse.ArgumentParser()
        subparsers = self.parser.add_subparsers()

        # Add subparsers from commands.

        for i in self.commands.values():
             i.install(subparsers.add_parser(i.name, add_help=False))


    def call(self, arguments=None):
        """Run stado with given arguments"""

        # Show help message if no arguments.

        #if len(sys.argv) == 1:
        #    #self.commands['help'].run()
        #    sys.exit(0)                         # 0 = successful termination

        # Arguments from sys.args or from method arguments.
        if not arguments:
            args = self.parser.parse_args()
        else:
            args = self.parser.parse_args(arguments.split())

        # Execute command.
        args = vars(args)
        print(args)
        if 'cmd' in args:


            cmd = args.pop('cmd')

            if cmd(**args):
                sys.exit(0)         # Success.
            else:
                sys.exit(1)         # Fail.
        return False