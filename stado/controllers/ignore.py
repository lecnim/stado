import fnmatch

from . import Controller


class Ignore(Controller):

    name = 'ignore'


    def __init__(self, site):
        Controller.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'loader.before_loading_content': self.ignore_file,
            'loader.before_loading_directory': self.ignore_file,
        })

        # List of ignored paths.
        self.ignored_paths = []


    def __call__(self, *paths):

        for path in paths:
            if not path in self.ignored_paths:
                self.ignored_paths.append(path)


    def ignore_file(self, path):

        for i in self.ignored_paths:
            if fnmatch.fnmatch(path, i):
                return False
