import os

class Command:

    name = ''
    summary = ''

    def __init__(self, user_interface):
        self.command_line = user_interface

    def install(self, parser):
        print('in', self.name)
        return parser

    def run(self, *args, **kwargs):
        pass


    @staticmethod
    def is_site(path):

        if os.path.isdir(path) and 'site.py' in os.listdir(path):
            return True
        return False


    def event(self, name):

        method = getattr(self.command_line, name)

        if isinstance(method, (list, tuple)):
            if len(method) == 2:
                method[0](*method[1])
            else:
                method[0](*method[1], **method[2])
        else:
            method()



import sys
import argparse


from .build import Build
from .watch import Watch
from .view import View
from .edit import Edit



class CommandLineInterface:

    def __init__(self):

        # Available commands.

        self.commands = {
            Build.name: Build(self),
            Watch.name: Watch(self),
            View.name: View(self),
            Edit.name: Edit(self)
        }

        # Create command line parser.

        self.parser = argparse.ArgumentParser()
        subparsers = self.parser.add_subparsers()

        # Add subparsers from commands.

        for i in self.commands.values():
            parser = subparsers.add_parser(i.name, add_help=False)
            i.install(parser)


    # Shortcuts to commands.

    def build(self, *args, **kwargs):
        self.commands['build'].run(*args, **kwargs)

    def watch(self, *args, **kwargs):
        self.commands['watch'].run(*args, **kwargs)

    def view(self, *args, **kwargs):
        self.commands['view'].run(*args, **kwargs)


    # Execute command.

    def __call__(self, arguments=None):
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
        if 'function' in args:


            cmd = args.pop('function')
            cmd(**args)

            #if cmd(**args):
            #    sys.exit(0)         # Success.
            #else:
            #    sys.exit(1)         # Fail.
        return False


    # Events:

    def set_interval(self, value):
        self.commands['watch'].file_monitor.interval = value

    def before_waiting(self):
        pass
    def stop_waiting(self):
        pass
        self.commands['watch'].stop()
        self.commands['view'].stop()
        self.commands['edit'].stop()

    def after_rebuild(self):
        pass


    def before_build(self):
        pass
    def after_build(self):
        pass


    def before_watch(self):
        pass
    def after_watch(self):
        pass



    def before_view(self):
        pass
    def after_view(self):
        pass

    def before_edit(self):
        pass
    def after_edit(self):
        pass