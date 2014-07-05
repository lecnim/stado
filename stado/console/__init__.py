import os
import sys
import argparse
import traceback

from ..errors import StadoError
from .. import log, config
from ..libs.events import EventHandler


class Event:
    def __init__(self, cmd, type, **kwargs):
        self.cmd = cmd
        self.type = type
        self.kwargs = kwargs

class CommandError(StadoError):
    """Raises when command generates error."""
    pass

class Command:
    """Base class for commands."""

    name = ''
    summary = ''

    def __init__(self):
        self.event = EventHandler()

    def install(self, parser):
        """Overwritten by inheriting class."""
        return parser

    def run(self, *args, **kwargs):
        """Overwritten by inheriting class."""
        pass


    @staticmethod
    def is_site(path):
        """Returns True if given path is pointing to site directory."""

        if os.path.isdir(path) and 'site.py' in os.listdir(path):
            return True
        return False

    def is_python_script(self, path):

        if os.path.isfile(path) and path.endswith('.py'):
            return True

        return False


    # def event(self, name):
    #     """Execute event method in Console object."""
    #
    #     method = getattr(self.console, name)
    #
    #     if isinstance(method, (list, tuple)):
    #         if len(method) == 2:
    #             method[0](*method[1])
    #         else:
    #             method[0](*method[1], **method[2])
    #     else:
    #         method()



# Commands modules.

from .build import Build
from .watch import Watch
from .view import View
from .edit import Edit
from .help import Help
from .new import New



class Console:

    def __init__(self):


        self.events = EventHandler()

        # Available commands.

        build = Build()
        build.event.subscribe(self.on_event)
        watch = Watch(build)
        watch.event.subscribe(self.on_event)

        view = View(build)
        view.event.subscribe(self.on_event)

        edit = Edit(build, watch, view)
        edit.event.subscribe(self.on_event)

        self.commands = {
            Build.name: build,
            Watch.name: watch,
            View.name: view,
            Edit.name: edit,
            Help.name: Help(),
            New.name: New(),
        }

        # Create command line parser.

        self.parser = argparse.ArgumentParser()
        subparsers = self.parser.add_subparsers()

        # Add subparsers from commands.

        for i in self.commands.values():
            # parser = subparsers.add_parser(i.name, add_help=False)
            # parser.add_argument('-d', '--debug', action="store_true")
            i.install_in_parser(subparsers)

    def __getitem__(self, item):
        return self.commands[item]


    # Shortcuts to commands.

    def build(self, *args, **kwargs):
        self.commands['build'].run(*args, **kwargs)

    def watch(self, *args, **kwargs):
        self.commands['watch'].run(*args, **kwargs)

    def view(self, *args, **kwargs):
        self.commands['view'].run(*args, **kwargs)

    def help(self, *args, **kwargs):
        self.commands['help'].run(*args, **kwargs)

    # on_view_start
    # on_build_start
    # on_edit_start
    # on_watch_start

    # Events:

    # console.subscribe('on_start', callable, *args, **kwargs)
    # console.event('on_start')

    # on_start
    # on_stop

    def on_event(self, event):
        self.events.notify(event)
        pass

    # Execute command.

    def __call__(self, arguments=None):
        """Run stado with given arguments"""

        # Show help message if no arguments.

        # print('')

        # No arguments!
        # if not len(sys.argv) > 1 and not arguments:
        #     self.help()
        #     return True

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
                return True
            except StadoError as error:
                msg = 'Oops! Error! Something went wrong:\n{}'
                log.error(msg.format(error))
                raise
                # traceback.print_exc()
                return False

        log.setLevel(config.log_level)
        return result



    # Other methods.

    def set_interval(self, value):
        """Sets watcher interval."""
        self.commands['watch'].file_monitor.check_interval = value


    # Events:

    def on_rebuild(self, path):
        pass

    def before_waiting(self):
        """Runs before waiting loop in command run() method."""
        pass

    def stop_waiting(self):
        """Stops waiting loop in commands. For example stops development server."""
        log.debug('Console stop all services!')
        log.debug('watch')

        if not self.commands['watch'].is_stopped:
            self.commands['watch'].stop()
        log.debug('view')
        self.commands['view'].stop()
        log.debug('edit')
        self.commands['edit'].stop()


    def stop(self):
        log.debug('Stopping all console services!')

        if not self.commands['watch'].is_stopped:
            self.commands['watch'].stop()
        log.debug('view')
        self.commands['view'].stop()
        # log.debug('edit')
        self.commands['edit'].stop()


    def after_rebuild(self):
        """Runs after site rebuild, usually by watcher."""
        pass
