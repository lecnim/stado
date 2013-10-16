import fnmatch
from . import Plugin


class Ignore(Plugin):

    name = 'ignore'


    def __init__(self, site):
        Plugin.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'loader.before_loading_content': self.ignore_file,
        })

        # List of ignored paths.
        self.paths = []


    def __call__(self, *paths):
        self.paths.extend(paths)


    def ignore_file(self, path):

        for i in self.paths:
            if fnmatch.fnmatch(path, i):
                return False