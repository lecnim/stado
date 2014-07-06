import sys
import argparse

from .. import log, config
from ..console.events import EventHandler, Event

from .errors import CommandError
from .cmds.build import Build
from .cmds.watch import Watch
from .cmds.view import View
from .cmds.edit import Edit
from .cmds.help import Help
from .cmds.new import New


class Console:

    def __init__(self):
        self.events = EventHandler()

        self.commands = {
            Build.name: Build(),
            Watch.name: Watch(),
            View.name: View(),
            Edit.name: Edit(),
            Help.name: Help(),
            New.name: New(),
        }

        # Every event in each command will run the on_event() method.
        for i in self.commands.values():
            i.event.subscribe(self.on_event)

        # Create command line parser.

        self.parser = argparse.ArgumentParser()
        subparsers = self.parser.add_subparsers()

        # Add subparsers from commands.

        for i in self.commands.values():
            i.install_parser(subparsers)

    def __getitem__(self, item):
        return self.commands[item]

    def on_event(self, event):
        """Commands send an event."""
        self.events.notify(event)
        pass

    # Execute command.

    def __call__(self, arguments=None):
        """Run stado with given arguments"""

        # Show help message if no arguments.

        # No arguments!
        if not len(sys.argv) > 1 and not arguments:
            self.parser.print_help()
            return True

        # Arguments from sys.args or from method arguments.
        if not arguments:
            args = self.parser.parse_args()
        else:
            args = self.parser.parse_args(arguments.split())

        # Execute command.
        args = vars(args)

        # Enable debug mode.
        if 'debug' in args and args.pop('debug'):
            log.setLevel('DEBUG')

        result = None
        if 'function' in args:

            cmd = args.pop('function')

            try:
                result = cmd(**args)
            except KeyboardInterrupt:
                log.info('Exiting stado, goodbye!')
                return True
            except CommandError as e:
                msg = 'Oops! Error! Something went wrong:\n{}'
                log.error(msg.format(e))
                return False

        log.setLevel(config.log_level)
        return result

    def stop(self):
        log.debug('Stopping all console services!')

        if self.commands['watch'].is_running:
            self.commands['watch'].cancel()
        if self.commands['view'].is_running:
            self.commands['view'].cancel()
        if self.commands['edit'].is_running:
            self.commands['edit'].cancel()

        log.debug('')