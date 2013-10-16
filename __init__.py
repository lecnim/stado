#import sys
#import argparse
#
#
#from .commands.build import Build
#from .commands.deploy import Deploy
#from .commands.view import View
#from .commands.run import Run
#
#
#class UserInterface:
#
#    def __init__(self):
#
#        # Available commands.
#
#        self.commands = {
#            Build.name: Build(),
#            Deploy.name: Deploy(),
#            View.name: View(),
#            Run.name: Run()
#        }
#
#        # Create command line parser.
#
#        self.parser = argparse.ArgumentParser()
#        subparsers = self.parser.add_subparsers()
#
#        # Add subparsers from commands.
#
#        for i in self.commands.values():
#             i.install(subparsers.add_parser(i.name, add_help=False))
#
#
#    def call(self, arguments=None):
#        """Run stado with given arguments"""
#
#        # Show help message if no arguments.
#
#        #if len(sys.argv) == 1:
#        #    #self.commands['help'].run()
#        #    sys.exit(0)                         # 0 = successful termination
#
#        # Arguments from sys.args or from method arguments.
#        if not arguments:
#            args = self.parser.parse_args()
#        else:
#            args = self.parser.parse_args(arguments.split())
#
#        # Execute command.
#        args = vars(args)
#        print(args)
#        if 'cmd' in args:
#
#
#            cmd = args.pop('cmd')
#
#            if cmd(**args):
#                sys.exit(0)         # Success.
#            else:
#                sys.exit(1)         # Fail.
#        return False


    ## Continue code execution.
    #
    #def stop_watching(self):
    #    """Stops watching for changes in sites."""
    #    self.generator.monitor.stop()
    #
    #def stop_serving(self):
    #    """Stops server."""
    #    server = self.generator.server
    #    if server:
    #        server.stop()
    #
    ## Events.
    #
    #def event_after_building(self):
    #    """Runs after build command."""
    #    pass
    #
    #def event_after_rebuilding(self):
    #    """Runs after rebuilding triggered by site monitor."""
    #    pass

#import sys
#from commands import UserInterface
#
#
#framework = UserInterface()
#
#if __name__ == "__main__":
#    if framework.call():
#        sys.exit(0)
#    else:
#        sys.exit(1)